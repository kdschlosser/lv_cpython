# RT-Thread RTOS

<img src="https://raw.githubusercontent.com/RT-Thread/rt-thread/master/documentation/figures/logo.png" width=40% style="float: center;" >

## What is RT-Thread?

[**RT-Thread**](https://www.rt-thread.io/) is an [open source](https://github.com/RT-Thread/rt-thread), neutral, and community-based real-time operating system (RTOS). RT-Thread has **Standard version** and **Nano version**. For resource-constrained microcontroller (MCU) systems, the Nano version that requires only 3 KB Flash and 1.2 KB RAM memory resources can be tailored with easy-to-use tools. For resource-rich IoT devices, RT-Thread can use the **online software package** management tool, together with system configuration tools, to achieve intuitive and rapid modular cutting, seamlessly import rich software packages; thus, achieving complex functions like Android's graphical interface and touch sliding effects, smart voice interaction effects, and so on.

### Key features

- Designed for resource-constrained devices, the minimum kernel requires only 1.2KB of RAM and 3 KB of Flash.
- A variety of standard interfaces, such as POSIX, CMSIS, C++ application environment.
- Has rich components and a prosperous and fast growing <a href="https://packages.rt-thread.org/en/">package ecosystem</a>
- Elegant code style, easy to use, read and master.
- High Scalability. RT-Thread has high-quality scalable software architecture, loose coupling, modularity, is easy to tailor and expand.
- Supports high-performance applications.
- Supports all mainstream compiling tools such as GCC, Keil and IAR.
- Supports a wide range of <a href="https://www.rt-thread.io/board.html">architectures and chips</a>.

## How to run LVGL on RT-Thread?

[中文文档](https://www.rt-thread.org/document/site/#/rt-thread-version/rt-thread-standard/packages-manual/lvgl-docs/introduction)

LVGL has registered as a [software package](https://packages.rt-thread.org/en/detail.html?package=LVGL) of RT-Thread. By using [Env tool](https://www.rt-thread.io/download.html?download=Env) or [RT-Thread Studio IDE](https://www.rt-thread.io/download.html?download=Studio), RT-Thread users can easily download LVGL source code and combine with RT-Thread project. RT-Thread community has port LVGL to several BSPs:

| BSP                                                                                                                               | Note                                                                                                                                              |
| --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| [QEMU simulator](https://github.com/RT-Thread/rt-thread/tree/master/bsp/qemu-vexpress-a9/applications/lvgl)                       | [Infineon psoc6-evaluationkit-062S2](https://github.com/RT-Thread/rt-thread/tree/master/bsp/Infineon/psoc6-evaluationkit-062S2/applications/lvgl) |
| [Visual Studio simulator](https://github.com/RT-Thread/rt-thread/tree/master/bsp/simulator/applications/lvgl)                     | [Renesas ra6m3-ek](https://github.com/RT-Thread/rt-thread/tree/master/bsp/renesas/ra6m3-ek/board/lvgl)                                            |
| [Nuvoton numaker-iot-m487](https://github.com/RT-Thread/rt-thread/tree/master/bsp/nuvoton/numaker-iot-m487/applications/lvgl)     | [Renesas ra6m4-cpk](https://github.com/RT-Thread/rt-thread/tree/master/bsp/renesas/ra6m4-cpk/board/lvgl)                                          |
| [Nuvoton numaker-pfm-m487](https://github.com/RT-Thread/rt-thread/tree/master/bsp/nuvoton/numaker-pfm-m487/applications/lvgl)     | [synwit swm341](https://github.com/RT-Thread/rt-thread/tree/master/bsp/synwit/swm341/applications/lvgl)                                           |
| [Nuvoton nk-980iot](https://github.com/RT-Thread/rt-thread/tree/master/bsp/nuvoton/nk-980iot/applications/lvgl)                   | [STM32H750 ART-Pi](https://github.com/RT-Thread/rt-thread/tree/master/bsp/stm32/stm32h750-artpi/applications/lvgl)                                |
| [Nuvoton numaker-m2354](https://github.com/RT-Thread/rt-thread/tree/master/bsp/nuvoton/numaker-m2354/applications/lvgl)           | [STM32F469 Discovery](https://github.com/RT-Thread/rt-thread/tree/master/bsp/stm32/stm32f469-st-disco/applications/lvgl)                          |
| [Nuvoton nk-n9h30](https://github.com/RT-Thread/rt-thread/tree/master/bsp/nuvoton/nk-n9h30/applications/lvgl)                     | [STM32F407 explorer](https://github.com/RT-Thread/rt-thread/tree/master/bsp/stm32/stm32f407-atk-explorer/applications/lvgl)                       |
| [Nuvoton numaker-m032ki](https://github.com/RT-Thread/rt-thread/tree/master/bsp/nuvoton/numaker-m032ki/applications/lvgl)         | [STM32L475 pandora](https://github.com/RT-Thread/rt-thread/tree/master/bsp/stm32/stm32l475-atk-pandora/applications/lvgl)                         |
| [Nuvoton numaker-hmi-ma35d1](https://github.com/RT-Thread/rt-thread/tree/master/bsp/nuvoton/numaker-hmi-ma35d1/applications/lvgl) | [NXP imxrt1060-evk](https://github.com/RT-Thread/rt-thread/tree/master/bsp/imxrt/imxrt1060-nxp-evk/applications/lvgl)                             |
| [Nuvoton numaker-iot-m467](https://github.com/RT-Thread/rt-thread/tree/master/bsp/nuvoton/numaker-iot-m467/applications/lvgl)     | [Raspberry PICO](https://github.com/RT-Thread/rt-thread/tree/master/bsp/raspberry-pico/applications/lvgl)                                         |
| [Nuvoton numaker-m467hj](https://github.com/RT-Thread/rt-thread/tree/master/bsp/nuvoton/numaker-m467hj/applications/lvgl)         |                                                                                                                                                   |

### Tutorials

- [Introduce about RT-Thread and how to run LVGL on RT-Thread in simulators](https://www.youtube.com/watch?v=k7QYk6hSwnc)
- [How to import a BSP project with latest code into RT-Thread Studio](https://www.youtube.com/watch?v=fREPLuh-h8k)
- [How to Use LVGL with RT-Thread Studio in STM32F469 Discovery Board](https://www.youtube.com/watch?v=O_QA99BxnOE)
- [RT-Thread Youtube Channel](https://www.youtube.com/channel/UCdDHtIfSYPq4002r27ffqPw)
- [RT-Thread documentation center](https://www.rt-thread.io/document/site/)
