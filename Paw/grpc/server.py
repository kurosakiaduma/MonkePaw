import grpc
from concurrent import futures
from ..proto import monke_pb2
from ..proto import monke_pb2_grpc

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
monke_pb2_grpc.add_MonkeTranslatorServicer_to_server(Paw(), server)
server.add_insecure_port("[::]:50051")  # Listen on all interfaces
server.start()

class Paw(monke_pb2_grpc.MonkeTranslatorServicer):
    def Translate(self, request, context):
        # Receive IR message here
        ir = request.ir
        # Convert IR back to Python data structures
        # Generate Python code using your logic
        python_code = generated_python_code
        return monke_pb2.PythonCode(code=python_code)
