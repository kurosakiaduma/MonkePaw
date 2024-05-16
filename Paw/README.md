# MonkePaw Compiler

MonkePaw is a custom programming language that is compiled using a combination of Go and Python. The frontend of the compiler, which handles lexing and parsing, is written in Go. The Intermediate Representation (IR) is then sent to the Python backend via gRPC, where it is converted into Python code.

## Table of Contents

1. Getting Started
2. Prerequisites
3. Installation
4. Usage
5. Contributing
6. License
7. Contact

## Getting Started

This section will guide you through setting up your system to run the MonkePaw compiler.

### Prerequisites

- Go (latest version)
- Python (3.7 or higher)
- gRPC

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/kurosakiaduma/monkepaw-compiler.git
   
2. Install the necessary Go packages
    ```go
   go get -u google.golang.org/grpc
   go get -u github.com/golang/protobuf/protoc-gen-go

3. Install the necessary Python packages
    ```bash
   cd Paw
   pip install -r requirements.txt
   
### Usage