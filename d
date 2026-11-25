[1mdiff --git a/src/game/unknown_camctl.cpp b/src/game/unknown_camctl.cpp[m
[1mindex ff19aab..a646509 100644[m
[1m--- a/src/game/unknown_camctl.cpp[m
[1m+++ b/src/game/unknown_camctl.cpp[m
[36m@@ -6,6 +6,7 @@[m
 // namespace named after that module and registers its functions with the module's key (openjoan.ini[m
 // [Hooks] Disable= and the logs use it), name and address unchanged.[m
 [m
[32m+[m[32m#include <cmath>[m
 #include <cstdint>[m
 #include "../original/helpers.hpp"[m
 #include <cstring>[m
[36m@@ -586,8 +587,16 @@[m [mstruct H {[m
         if (global<std::int32_t>(d::g_control_mode) != 3)[m
             state[5] = joan::orig::arg::as<std::uint32_t>(joan::orig::as_unit(unit)->mounted()) != 0 ? global<std::uint32_t>(d::g_a0bbec) : global<std::uint32_t>(d::g_a0bbe8);  // 0x00430190[m
         state[7] = joan::orig::arg::as<std::uint32_t>(joan::orig::as_unit(unit)->mounted()) != 0 ? global<std::uint32_t>(d::g_a0bbf4) : global<std::uint32_t>(d::g_a0bbf0);[m
[31m-        const float follow_fov_tan = 3.0f;  // About 71.6 degrees vertical[m
[31m-        std::memcpy(&state[8], &follow_fov_tan, sizeof(follow_fov_tan));[m
[32m+[m[32m                jo::CamParams follow_camera;[m
[32m+[m[32m        std::memcpy(&follow_camera, state, sizeof(follow_camera));[m
[32m+[m
[32m+[m[32m        const float shoulder_offset = 15.0f;[m
[32m+[m[32m        const float yaw = follow_camera.orbit[0];[m
[32m+[m[32m        follow_camera.position[0] += std::sin(yaw) * shoulder_offset;[m
[32m+[m[32m        follow_camera.position[1] -= std::cos(yaw) * shoulder_offset;[m
[32m+[m[32m        follow_camera.fov_tan = 1.0f;[m[41m  [m
[32m+[m
[32m+[m[32m        std::memcpy(state, &follow_camera, sizeof(state));[m
         if ((joan::orig::arg::as<std::int32_t>(joan::orig::state_differs(joan::orig::arg::mptr(static_cast<void*>(state)), joan::orig::arg::mptr(static_cast<void*>(&jo::self<jo::CameraFollow>(this)->motions->to)))) & 0xff) != 0)  // 0x0041a900[m
             joan::orig::as_camera_motion(jo::view<void*>(jo::self<jo::CameraFollow>(this)->motions))->start(joan::orig::arg::mptr(static_cast<void*>(&jo::self<jo::CameraFollow>(this)->camera->params)), joan::orig::arg::mptr(static_cast<void*>(state)));  // 0x00423ec0[m
         return 1;[m
