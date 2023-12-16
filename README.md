<div align="center">
<h1> AI Want Coffee: Using GPT to make coffee ☕ </h1>

<!-- <--!span><font size="5", > Efficient and Robust 2D-to-BEV Representation Learning via Geometry-guided Kernel Transformer
</font></span> -->

  Alefe Gadioli, Breno, Daniel, Eduardo, Mariana e Matheus Rezende
<!-- <a href="https://scholar.google.com/citations?user=pCY-bikAAAAJ&hl=zh-CN">Jinwei Yuan</a> -->
<div><a href="https://arxiv.org/abs/2208.11434">[AI Want Coffee Report]</a></div> 

</div>

# Introduction

The 'AI Want Coffee' project assesses the potential of Artificial General Intelligence (AGI) using the 'Wozniak test', which challenges a robot to enter a house, make and serve coffee. It incorporates skills such as autonomous navigation and speech recognition. The focus is on testing OpenAI's GPT-4 model in real scenarios, exploring how its natural language processing and response generation can aid in developing AGI for complex tasks in unstructured environments.

A. **Coffee-Assistant:** This architecture assists the user in preparing coffee by suggesting the next steps. It starts with the user sending an image of the kitchen to GPT-4, which then formulates a list of procedures. After each action completed by the user, a new image is sent to GPT-4 for evaluation and to suggest the next step. The process heavily relies on human feedback.

B. **Coffee-Agent:** Unlike Coffee-Assistant, Coffee-Agent aims to allow GPT to act autonomously, controlling a robotic body with a set of defined instructions. A human substitutes the robotic body, following GPT's instructions. Initially, GPT receives a photo of the human's view in the kitchen, and in each iteration, it calls a predefined function, sending a new photo after each completed instruction.

C. **Coffee-Agent v2:** This version seeks to solve problems from the previous architecture, such as impossible mission requests. It's an evolution that enhances the functioning and autonomy of the system.

<div align="center"> <a href="https://ibb.co/1nHr279"><img src="https://i.ibb.co/dcnPKjQ/Whats-App-Image-2023-12-03-at-13-37-41.jpg" alt="Whats-App-Image-2023-12-03-at-13-37-41" border="0"></a> </div>

## Results
Tests were conducted in different kitchens, for testing in different scenarios using cameras and sending to the GPT. 

### Visualization  **adicionar imagens**
<div align="center"><td><img src=data/sample_videos/cozinha01(1).gif/></td></div>

# Installation
## 1. Prerequisites

- Python 3.6 or higher
- IP Webcam with RTSP enabled

## 2. Environment Setup
### 1. Install Python 3.6 or higher:
- **Windows:** Download the installer from <a href="https://www.python.org/downloads/">the official Python website</a>
- **Linux:** Use your distribution's package manager, for example:
``` shell
# Python3 - Linux
sudo apt-get install python3
```

### 2. Clone the Repository:
- Open a terminal
``` shell
# ai-want-coffee
git clone https://github.com/lewislf/ai-want-coffee.git
```

### 3. Install Dependencies:
- Open a terminal and navigate to the cloned project directory.
 ``` shell
# Open the Folder
cd ai-want-coffee
```
-  Install all required dependencies
``` shell
# ai-want-coffee
pip install -r requirements.txt
```

## 3. Project Configuration
- Obtain an API Key from OpenAI by creating an account at <a href="https://openai.com/">OpenAI</a>.
- Open the file named api_key.py in the project directory and define OPENAI_API_KEY with your key and Replace the ip and port in the ip_address variable with your IP webcam's information, in the LOCAL_CAMERA variable.
``` shell
# api_key.py
OPENAI_API_KEY = 'YOUR API KEY'
LOCAL_CAMERA = "rtsp://ip:port/h264_ulaw.sdp" 
```

## 4. Execution
### 1. Run the Script:
- Open de folder **predict**:
 ```shell
# ai-want-coffee/predict/
cd ai-want-coffee/predict/
```
- In the terminal, execute python gpt.py
```shell
# Navigate to the ai-want-coffee repository and execute the following:
python3 gpt.py
```


# Future Works
Explore how to eliminate the "interact" function that was made available to the Coffee-Agent, since it is classified as an abstract order. Works that are outside the scope of the AGI subject, but continue from what was produced: Improve integration with Coffee-Assistant through the voice communication module we developed. Use it for tasks other than making coffee. Integration with VR glasses.
