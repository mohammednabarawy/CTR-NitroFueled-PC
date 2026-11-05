// Driverless collaborators for the production Presenter::Present method. This fixture does
// not implement interpolation or Vulkan synchronization: events expose the orchestration.
#include <algorithm>
#include <cassert>
#include <chrono>
#include <condition_variable>
#include <cstdio>
#include <cstdint>
#include <limits>
#include <mutex>
#include <queue>
#include <string>
#include <thread>
#include <vector>

using u64 = std::uint64_t;
std::vector<std::string> events;
namespace vk {
using Image = int;
using Semaphore = int;
enum class Result { eSuccess };
struct SemaphoreWaitInfo { unsigned semaphoreCount; const Semaphore* pSemaphores; const u64* pValues; };
enum class PresentModeKHR { eFifo, eMailbox };
std::string to_string(PresentModeKHR mode) { return mode == PresentModeKHR::eFifo ? "Fifo" : "Mailbox"; }
}
#define ASSERT_MSG(condition, ...) assert(condition)
void Check(int result) { assert(result == 0); }
namespace BbOverlay {
bool open = false;
bool MenuOpen() { return open; }
}
struct DebugStateFake { int flips = 0; void IncFlipFrameNum() { ++flips; } } DebugState;
struct SemaphoreFake { int Handle() { return 7; } };
struct SubmitInfo {
    void AddWait(vk::Semaphore semaphore, u64 tick = 1) {
        events.push_back(semaphore == 9 ? "wait-acquire" : "wait-producer");
        assert(semaphore == 9 ? tick == 1 : tick == 10);
    }
    void AddSignal(int handle) {
        events.push_back(handle == 11 ? "signal-fence" : "signal-present");
    }
};
struct SchedulerFake {
    SemaphoreFake semaphore;
    SemaphoreFake* GetWorkSemaphore() { return &semaphore; }
    void WaitSubmitted(u64) { events.push_back("producer-submitted"); }
    void Wait(u64) { events.push_back("generated-complete"); }
    void Finish() { events.push_back("finish"); }
    u64 CurrentTick() { return 1; }
    void Flush(SubmitInfo&) { events.push_back("submit"); }
};
struct DeviceFake {
    vk::Result resetFences(int fence) {
        assert(fence == 11);
        events.push_back("reset-fence");
        return vk::Result::eSuccess;
    }
    int waitSemaphores(vk::SemaphoreWaitInfo info, u64) {
        assert(*info.pValues == 10);
        events.push_back("producer-complete");
        return 0;
    }
};
struct InstanceFake { DeviceFake GetDevice() { return {}; } };
struct FrameGenFake {
    struct Inputs {
        unsigned slot; vk::Image color; int color_format; unsigned width, height;
        float frame_ms; bool reset;
    };
    bool enabled = true;
    bool reset = false;
    bool Record(Inputs in) {
        events.push_back("record");
        reset = in.reset;
        return enabled && in.color && !in.reset;
    }
    vk::Image OutputImage(unsigned) { return 2; }
};
struct SwapchainFake {
    vk::PresentModeKHR mode = vk::PresentModeKHR::eFifo;
    struct Format { int format = 1; };
    Format GetSurfaceFormat() { return {}; }
    vk::PresentModeKHR GetPresentMode() { return mode; }
    int GetImageAcquiredSemaphore() { return 9; }
    int GetPresentReadySemaphore() { return 12; }
};
struct Frame {
    vk::Semaphore ready_semaphore = 7;
    u64 ready_tick = 10;
    int present_done = 11;
    vk::Image image = 1;
    unsigned id = 0, width = 1920, height = 1080;
    bool is_hdr = false;
    std::chrono::steady_clock::time_point prepared_at{std::chrono::milliseconds(1000)};
};
class Presenter {
public:
    void Present(Frame* frame, bool is_reusing_frame = false, bool is_game_frame = true);
    void SubmitPresentImage(Frame* frame, bool real_frame);
    bool AcquirePresentImage() {
        events.push_back("acquire");
        const bool result = acquisitions.empty() || acquisitions.front();
        if (!acquisitions.empty()) acquisitions.pop();
        return result;
    }
    bool PresentImage(Frame* frame, vk::Image image, bool real_frame) {
        assert(image == (real_frame ? 1 : 2));
        SubmitPresentImage(frame, real_frame);
        events.push_back(real_frame ? "real" : "generated");
        if (real_frame && swapchain.mode == vk::PresentModeKHR::eMailbox) {
            assert(std::chrono::steady_clock::now() - generated_at >= std::chrono::milliseconds(7));
        }
        if (!real_frame) generated_at = std::chrono::steady_clock::now();
        return real_frame ? real_success : generated_success;
    }
    Frame* last_submit_frame = nullptr;
    std::queue<Frame*> free_queue;
    std::mutex free_mutex;
    std::condition_variable free_cv;
    InstanceFake instance;
    SchedulerFake draw_scheduler, present_scheduler;
    FrameGenFake framegen;
    SwapchainFake swapchain;
    std::chrono::steady_clock::time_point last_generated_input{};
    float framegen_interval_ms = 16.6f;
    bool framegen_reset = true;
    u64 generated_present_count = 0;
    std::queue<bool> acquisitions;
    bool generated_success = true, real_success = true;
    std::chrono::steady_clock::time_point generated_at{};
};

// @PRESENTER_IMPLEMENTATION@

int count(const char* event) { return std::count(events.begin(), events.end(), event); }
bool before(const char* a, const char* b) {
    const auto first = std::find(events.begin(), events.end(), a);
    const auto second = std::find(events.begin(), events.end(), b);
    return first != events.end() && second != events.end() && first < second;
}
int main(int argc, char** argv) {
    assert(argc == 2);
    const std::string test = argv[1];
    Presenter p;
    Frame frame;
    // Warm the history through the same entry point before testing a generated pair.
    p.Present(&frame);
    assert(count("record") == 1 && count("generated") == 0 && count("real") == 1);
    events.clear();
    p.free_queue.pop();
    frame.prepared_at += std::chrono::milliseconds(16);
    DebugState.flips = 0;
    if (test == "off") p.framegen.enabled = false;
    if (test == "menu") BbOverlay::open = true;
    if (test == "minimized") p.acquisitions.push(false);
    if (test == "generated-failure") p.generated_success = false;
    if (test == "reacquire-failure") { p.acquisitions.push(true); p.acquisitions.push(false); }
    if (test == "real-failure") p.real_success = false;
    if (test == "mailbox") p.swapchain.mode = vk::PresentModeKHR::eMailbox;
    if (test == "gap") frame.prepared_at += std::chrono::milliseconds(200);
    if (test == "hdr") frame.is_hdr = true;
    if (test == "native") frame.ready_semaphore = 8;
    p.Present(&frame, test == "reuse", test != "nongame");

    if (test == "history" || test == "mailbox" || test == "native") {
        assert(before("record", "generated") && before("generated", "real"));
        assert(count("generated") == 1 && count("real") == 1);
        assert(p.generated_present_count == 1 && DebugState.flips == 1);
        if (test == "native") assert(count("producer-submitted") == 0);
        else assert(before("producer-submitted", "record"));
        assert(before("generated", "generated-complete") &&
               before("generated-complete", "real"));
    } else if (test == "minimized") {
        assert(count("record") == 0 && count("real") == 0);
        assert(before("producer-submitted", "producer-complete") && p.framegen_reset);
    } else if (test == "generated-failure" || test == "reacquire-failure") {
        assert(count("generated") == 1 && count("real") == 0);
        assert(before("generated", "finish") && before("finish", "producer-complete"));
        assert(p.framegen_reset && DebugState.flips == 0);
        assert(p.generated_present_count == 0);
    } else if (test == "real-failure") {
        assert(before("generated", "real") && p.framegen_reset);
        assert(p.generated_present_count == 0);
    } else {
        assert(count("generated") == 0 && count("real") == 1);
        if (test == "gap") assert(p.framegen.reset);
        if (test == "reuse" || test == "nongame" || test == "menu") {
            assert(count("record") == 0 && p.framegen_reset);
        }
    }
    assert(count("reset-fence") == count("real"));
    assert(count("signal-fence") == count("real"));
    assert(count("wait-producer") == count("generated") + count("real"));
    assert(count("wait-acquire") == count("generated") + count("real"));
    assert(p.free_queue.size() == (test == "reuse" ? 0 : 1));
}
