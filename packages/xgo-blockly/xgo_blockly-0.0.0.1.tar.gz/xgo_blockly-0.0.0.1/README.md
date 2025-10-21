# XGO Blockly 图形化编程服务器

## 简介

XGO Blockly 是专为陆吾 XGO 机器人系列设计的图形化编程和 AI 编程服务器。通过简单的安装和启动,您可以在电脑浏览器中进行图形化编程,AI 编程,控制您的陆吾 XGO机器人。

## 支持的机型

- **XGO-Lite**：轻量级四足机器狗,680g超轻设计,适合教育入门
- **XGO-Mini**：十二自由度AI机器狗,配备机械臂和500万像素摄像头,支持AI视觉和语音识别
- **XGO-Rider**：双轮足开源开发平台,基于树莓派,560g桌面级设计,支持AI边缘计算、自稳控制和地形跨越

- **未来的机型将陆续加入。**

## 安装要求

该 pip 包需要安装在陆吾 XGO 机器人系列的树莓派机器上。

## 安装步骤

1. **进入指定目录**
   ```bash
   cd /home/pi/RaspberryPi-CM5/
   ```

2. **创建或激活虚拟环境**
   
   首先检查是否已存在 `blocklyvenv` 虚拟环境：
   ```bash
   ls blocklyvenv
   ```
   
   如果不存在，请创建虚拟环境（注意：使用 `--system-site-packages` 参数确保继承系统包，避免 Picamera2 和 libcamera 依赖问题）：
   ```bash
   python3 -m venv --system-site-packages blocklyvenv
   ```
   
   激活虚拟环境：
   ```bash
   source blocklyvenv/bin/activate
   ```

3. **安装 xgo-blockly 包**
   ```bash
   pip install xgo-blockly -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```
   
   **升级 xgo-blockly 包**（如果已安装）：
   ```bash
   pip install --upgrade xgo-blockly -i https://pypi.tuna.tsinghua.edu.cn/simple
   pip install protobuf==4.25.8 -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

4. **单独安装 AI 识别依赖包**
   
   由于包冲突的原因，需要单独安装 MediaPipe 等几个包：
   ```bash
   pip install onnxruntime==1.20.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
   pip install mediapipe -i https://pypi.tuna.tsinghua.edu.cn/simple
   如果安装 tensorflow 时，报错，请先清理缓存：pip cache purge
   pip install tensorflow==2.15.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
   pip install ml_dtypes==0.5.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

## 启动服务

安装成功后，运行以下命令启动图形化编程和AI编程服务器：

```bash
xgo-blockly
```

## 使用方法

服务器启动后，在电脑上打开浏览器，访问树莓派的IP地址和端口号（默认端口号为8000，直接输入IP即可）即可开始图形化编程和AI编程。

## 功能特性

- 🎯 **图形化编程**：拖拽式编程界面，简单易用
- 🤖 **AI编程辅助**：智能代码生成和优化建议
- 🔗 **实时控制**：直接控制陆吾机器人硬件
- 🌐 **Web界面**：跨平台浏览器访问
- 📱 **响应式设计**：支持电脑、平板等设备

## 技术支持

如有问题或需要技术支持,请联系陆吾机器人技术团队。

联系方式: hello@xgorobot.com

---

# XGO Blockly Visual Programming Server

## Introduction

XGO Blockly is a visual programming and AI programming server designed specifically for the Luwu XGO robot series. Through simple installation and startup, you can perform visual programming and AI programming in your computer browser to control your Luwu XGO robot.

## Supported Models

- **XGO-Lite**: Lightweight quadruped robot dog, ultra-light 680g design, suitable for educational introduction
- **XGO-Mini**: Twelve degrees of freedom AI robot dog, equipped with robotic arm and 5-megapixel camera, supporting AI vision and voice recognition
- **XGO-Rider**: Wheeled-legged open source development platform, based on Raspberry Pi, 560g desktop-level design, supporting AI edge computing, self-balancing control and terrain crossing

- **More models will be added in the future.**

## Installation Requirements

This pip package needs to be installed on the Raspberry Pi of the Luwu XGO robot series.

## Installation Steps

1. **Navigate to the specified directory**
   ```bash
   cd /home/pi/RaspberryPi-CM5/
   ```

2. **Create or activate virtual environment**
   
   First check if the `blocklyvenv` virtual environment already exists:
   ```bash
   ls blocklyvenv
   ```
   
   If it doesn't exist, create the virtual environment (Note: Use the `--system-site-packages` parameter to ensure inheritance of system packages and avoid Picamera2 and libcamera dependency issues):
   ```bash
   python3 -m venv --system-site-packages blocklyvenv
   ```
   
   Activate the virtual environment:
   ```bash
   source blocklyvenv/bin/activate
   ```

3. **Install xgo-blockly package**
   ```bash
   pip install xgo-blockly
   ```
   
   **Upgrade xgo-blockly package** (if already installed):
   ```bash
   pip install --upgrade xgo-blockly
   pip install protobuf==4.25.8
   ```

4. **Install AI recognition dependencies separately**
   
   Due to package conflicts, MediaPipe and several other packages need to be installed separately:
   ```bash
   pip install onnxruntime==1.20.0
   pip install mediapipe
   # If there's an error when installing tensorflow, please clear the cache first: pip cache purge
   pip install tensorflow==2.15.0
   pip install ml_dtypes==0.5.0
   ```

## Starting the Service

After successful installation, run the following command to start the visual programming and AI programming server:

```bash
xgo-blockly
```

## Usage

After the server starts, open a browser on your computer and visit the Raspberry Pi's IP address and port number (default port is 8000) to begin visual programming and AI programming.

## Features

- 🎯 **Visual Programming**: Drag-and-drop programming interface, simple and easy to use
- 🤖 **AI Programming Assistant**: Intelligent code generation and optimization suggestions
- 🔗 **Real-time Control**: Direct control of Luwu robot hardware
- 🌐 **Web Interface**: Cross-platform browser access
- 📱 **Responsive Design**: Supports computers, tablets and other devices

## Technical Support

If you have any questions or need technical support, please contact the Luwu Robotics technical team.

Contact: hello@xgorobot.com