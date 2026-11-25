# OpenJoan game engine development

Open the repository root in VS Code and install the recommended **CMake Tools** and **C/C++** extensions. Build with a native Linux x86-64 toolchain. Install GDB and Python 3 for the launch tasks. [Build prerequisites](README.md#quick-start-on-native-linux)

## Build, run, and debug

Point `game` at your Steam game directory, then run these commands in Bash from
the repository root. They copy only the runtime data directories to a local
`play/` folder. If you already have a private staged copy, you can place those
directories in `play/` directly.

```bash
game="/absolute/path/to/your/Steam/game"
mkdir -p play
cp -a --reflink=auto -- "$game"/{Resource,anim,des,font,images,int8x6,item,item_des,map,model,movie,music,scenario,script,shader,texture,unit} play/
```

1. In **Run and Debug**, choose **OpenJoan: Linux Debug (GDB)**. Press **F5** to configure, build, stage, and launch the native executable in `run/debug/`.
2. For CMake Tools, use **CMake: Select Configure Preset** and select **VS Code Linux Debug**. Use the corresponding build preset if you build from the CMake sidebar. CMake Tools supplies the active target's IntelliSense settings, with each build's `compile_commands.json` available as a fallback. Select the matching **Linux Debug** or **Linux Release** configuration in the C/C++ status bar.
3. Use **OpenJoan: Linux Release (GDB)** to build and launch the optimized player configuration. Use **Ctrl+F5** to launch without stopping in the debugger. **Terminal → Run Build Task** runs the Debug build and stage task without launching.

| Configuration | CMake build tree | Runtime directory | Compiler and engine settings |
| --- | --- | --- | --- |
| Linux Debug | `build/vscode-linux-debug/` | `run/debug/` | CMake `Debug`, full symbols, `JOAN_RELEASE=OFF`. The preset explicitly aligns functions to 16 bytes for the legacy call dispatcher. Warnings remain visible and are nonfatal. |
| Linux Release | `build/vscode-linux-release/` | `run/release/` | `RelWithDebInfo`, optimized with symbols, `JOAN_RELEASE=ON`. This follows upstream's player build. |

The two runtime directories use hard links to share data in `play/` without duplicating it. Each has its own executable, INI, saves, and generated caches. Existing `.PLN` terrain caches are seeded as private copies because the engine can rewrite them. The build task keeps local INI changes and file overrides. For content experiments, replace a hard link in `run/debug/` with a private copy before editing it. Writing directly to the linked file changes the shared asset.

The VS Code presets use separate build trees and leave `JOAN_INSTALL_DIR` empty. They use the system SDL3, OpenAL and FFmpeg libraries. CMake fetches the pinned FreeType source unless you provide an extracted copy with `FETCHCONTENT_SOURCE_DIR_FREETYPE`. From the repository root, `python3 .vscode/build_and_stage.py debug` runs the same build and stage steps as F5.

[Workspace presets](CMakePresets.json) · [Launch configurations](.vscode/launch.json) · [Build and stage script](.vscode/build_and_stage.py)

### First GDB breakpoint

1. Open `src/runtime/loader/joan_re.cpp`. In `run()`, click the gutter at the line containing `std::filesystem::current_path(g_dir, ec)`.
2. Launch Debug with F5. Expand **Variables → Locals** and inspect `g_dir`, or use `-exec print g_dir` in the Debug Console. It should point to `run/debug/`. Use **F10** to step over the directory change, then F5 to continue.
3. Put a second breakpoint on the elapsed-time assignment in `Game::run`. Inspect `now` and `previous` in **Watch**. Disable this breakpoint after the first hit so it stops interrupting the game every frame.
4. To inspect one rendering event, add a conditional breakpoint in `Device::DrawIndexedPrimitive` with `prim_count > 1000`. Inspect `prim`, `start_index`, and the call stack when a matching draw arrives.

[Loader entry](src/runtime/loader/joan_re.cpp) · [Game loop](src/game/unknown_game_run.cpp) · [Indexed draws](src/gl/device.cpp)

## In-game developer tools

| Tool | How to use it |
| --- | --- |
| Developer menu | In the focused Debug game window, press **backtick**. Use **Up/Down** to select, **Enter/Right** to activate, and **Esc/Backspace** to go back or close. **Missions** loads a campaign mission. **Hero stats**, **Spawn**, and **Cheats** work with an active mission. The stat panel shows the current player character's values. |
| Rendering controls | The menu’s **Ambient occlusion** page can switch between off, normal, and occlusion-only display and tune radius, strength, and distance. **Shadows** can compare the original stencil volumes with the debug shadow-map path. Enable the normal in-game Shadows option first. Tuning is live for the session. The engine logs values you can transfer to the INI. |
| Free camera | In a mission, close the developer menu and press **F9**. Use **W/A/S/D** to move, **Q/E** for down/up, **Shift/Ctrl** for faster/slower travel, and the **arrow keys** or **right mouse drag** to turn. F9 hands control back to the game. |
| Screenshot and logs | **F11** writes `openjoan_shotNNN.bmp` in the runtime folder. **F12** opens Mission Brief. Debug defaults enable `[Hooks] Log=1`. Read `run/debug/openjoan_loader.log` for startup and `run/debug/openjoan.log` for the subsystem and developer-menu messages. |

Edit `run/debug/openjoan.ini` between launches. `[Graphics] PerfLog=5` logs frame timing and draw statistics every five seconds. `GLDebug=1` requests a GL debug context, logs driver diagnostics, and captures selected frames. `[Debug] HitchLog=33` logs frames exceeding 33 ms. `AnimCensus=5` reports sampled animation activity, and `ImportCensus=1` writes an import-call report on exit. The upstream sampling profiler controlled by `Profile` is Windows/MSVC-only. Some old notes refer to `DrawProfile` and related keys. The current registry marks those keys retired.

[Developer menu](src/debug_menu.cpp) · [Free camera](src/freecam.cpp) · [Debug INI template](src/openjoan.ini) · [Runtime diagnostics](docs/RUNTIME.md)

### Legacy console and developer keys

The legacy console is a separate text input from OpenJoan's menu. The source enables it when you type **coronation** on the main menu, outside the settings and save dialogs. In a mission, enter **tilde** (`~`), then type a command and press **Enter**. **Esc** closes the prompt, and **Up/Down** walks its history. If the same physical key opens the developer menu, set `[Debug] MenuKey=119` to move that menu to F8 before restarting. The activation path is established from source, with keyboard behavior dependent on the layout's legacy key translation.

Try these on a disposable Debug profile:

| Command | Effect |
| --- | --- |
| `unit_add_gold 1000` | Adds gold to the current hero. Also available as **Hero stats → Gold +1000**. |
| `unit_add_str 10` | Adds strength to the current hero. |
| `invincible 1` / `invincible 0` | Enables or disables invincibility. |
| `toggle_fog_of_war` | Toggles fog of war. |
| `hp` / `ep` | Refreshes the current unit’s health or energy. |

The old developer hotkey switch is separate again. The game checks for `super_cheat_mode.sys` in its runtime folder and uses **Home** to toggle that switch. The source includes **u** to cycle fill mode and **t** to advance the mission. The legacy `DebugOverlay` draw and input methods are no-ops in this build. Use the OpenJoan menu and the renderer log for inspection. For reproducibility tests, Debug also supports `--record FILE` and `--replay FILE`. Use the same data, settings, and save state for both runs.

[Console unlock](src/game/unknown_mainmenu.cpp) · [Keyboard dispatch](src/game/unknown_game_input.cpp) · [Console command parser](src/game/unknown_cheats.cpp) · [Replay options](docs/RUNTIME.md)

## Model and asset tools

Run **Terminal → Run Task → OpenJoan: Build asset tools**, then use the workspace terminal:

```bash
tools=build/vscode-linux-debug/tools
"$tools/jview" --game-dir "$PWD/play" 'unit/Joan_of_Arc.AM1' \
  --anim 'anim/joan_of_arc.am2'
"$tools/jmodel" play/unit/Joan_of_Arc.AM1
```

`jview` displays loose `.SMO` and `.AM1` models and can play `.AM2` animation clips. Left drag orbits, right drag pans, and the wheel zooms. **Space** pauses, **Left/Right** changes animation, **Up/Down** changes playback speed, and **comma/period** steps through time. **B** toggles bones, **W** wireframe, **G** grid, **Page Up/Down** the model, and **Home** resets the view. `jmodel` prints model metadata and can export a posed Wavefront OBJ. `jres` lists or extracts resource banks and `jdbf` inspects resource database tables.

[Viewer source](tools/jview.cpp) · [Exporter source](tools/jmodel.cpp) · [Asset tool reference](tools/README.md)

## Architecture reading map

| Start with | What to trace |
| --- | --- |
| [Game loop](src/game/unknown_game_run.cpp) and [game tick](src/game/unknown_game_tick.cpp) | SDL-backed input, screen transitions, drawing, then a variable-time update. The legacy 30 Hz frame scale is a unit of time. |
| [Unit resources](src/game/unitres.cpp), [unit manager](src/game/unknown_units_mgr.cpp), and [unit update](src/game/unknown_unitupd.cpp) | Resource definitions become live records identified by `recno`. A scene actor represents a unit visually. The scheduler groups units by distance and distributes update work. |
| [Unit AI](src/game/unknown_ur_orders.cpp), [path space](src/enpath/pathsp.cpp), and [physics](src/enphysic/physys.cpp) | An order or script assigns a task. AI selects a response, navigation finds a polygonal route, and physics checks the displacement and floor. |
| [Render call tree](docs/render/EN3D_RENDER.md), [OpenGL device](src/gl/device.cpp), and [shader generation](src/gl/shaders.cpp) | Camera → scene → plane → Direct3D 8-shaped draw → OpenGL state and GLSL. End-of-frame work includes effects, HUD composition, and presentation. |
| [Mission scripts](docs/scripting/LANGUAGE.md) and [interpreter](src/uti3d/esstate2.cpp) | The `.sce` parser builds statement objects that issue gameplay commands, play dialogue, and suspend at `WAIT` until a later game tick. |
| [Startup and layout](docs/ARCHITECTURE.md) and [x64 design](docs/X64.md) | `JOAN_REPLACE` associates reconstructed C++ with the original function address. The loader relocates the typed data image and runs the replacement functions through the registered call graph. |

## Beginner exercises

1. **Tune camera acceleration in C++.** In `freecam.cpp`, find the Shift multiplier in `frame()`. Set a breakpoint on the next movement calculation and compare `g.speed`, `dt`, and the local `speed` with the game focused. Change the Shift multiplier from `5.0f` to `3.0f`, rebuild with F5, and compare movement over the same interval. Restore the multiplier when finished. [Free-camera movement](src/freecam.cpp)
2. **Connect an overlay action to gameplay.** Start a mission and break in `console_execute()`. Choose **Hero stats → Gold +1000** in the developer menu, inspect `cmd` and the stack, then continue and confirm the value changes in-game. Change the grant to 500 in `debug_menu.cpp` and update the menu and status text to match. This exercises UI input, command parsing, and a gameplay mutation without changing the unit layouts. [Developer actions](src/debug_menu.cpp) · [Console parser](src/game/unknown_cheats.cpp)
3. **Measure a graphics toggle.** Enable `PerfLog=5` in the Debug INI. Compare the same view with the AO menu on and off. Record frame time and draw count, and use isolation mode to see which pixels receive occlusion. Keep the camera and scene fixed during both samples. [Ambient occlusion implementation](src/render/ambient_occlusion.cpp)
4. **Make an isolated script change.** After staging Debug once, copy mission 1’s script over its runtime link before editing:

   ```bash
   script=run/debug/script/scenario/S1L1.sce
   if [ "$script" -ef play/script/scenario/S1L1.sce ]; then
     cp --remove-destination -- play/script/scenario/S1L1.sce "$script"
   fi
   ```

   Find `set_fog_distance` in the private file and change only its numeric argument. Reload the mission, compare visibility, and follow the command through the built-ins table. Keep the shared `play/` script as the baseline. [Script built-ins](docs/scripting/BUILTINS.md)
