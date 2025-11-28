import netsquid as ns
import random

from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta


class AliceProgram(Program):
    NODE_NAME = "Alice"
    PEER_BOB = "Bob"

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name=f"program_{self.NODE_NAME}",
            csockets=[self.PEER_BOB],
            epr_sockets=[self.PEER_BOB],
            max_qubits=2,
        )

    def run(self, context: ProgramContext):
        # get classical sockets
        csocket_bob = context.csockets[self.PEER_BOB]
        # get EPR sockets
        epr_socket_bob = context.epr_sockets[self.PEER_BOB]
        # get connection to QNPU
        connection = context.connection

        print(f"{ns.sim_time()} ns: Hello from {self.NODE_NAME}")
        results = []
        bases = []

        for i in range(100):

            epr_qubit = epr_socket_bob.create_keep()[0] # Mando el par a Bob
            
            if random.randint(0, 1) == 1:
                epr_qubit.H()  # Aplico una puerta X 
                base = 'X'
            else:    
                base = 'Z'
            result = epr_qubit.measure()  # Mido el qubit

            yield from connection.flush() # Mando las intrucciones al Quantum Network Processor Unit
            results.append(int(result))
            bases.append(base)

        csocket_bob.send(bases) # Mando los resultados a Bob
        bases_bob = yield from csocket_bob.recv()  # Recibo los resultados de Bob
        # print(f"{ns.sim_time()} ns: Bases from Bob: {bases_bob}")

        raw_key = []
        for i in range(100):
            if bases_bob[i] == bases[i]:
                raw_key.append(results[i])
        print(f"{ns.sim_time()} ns: Raw key established by {self.NODE_NAME}: {raw_key}")

        errors = 0

        nums_to_del = raw_key[::2]
        n = len(nums_to_del)
        csocket_bob.send(nums_to_del) # Mando la mitad de los bits a Alice
        nums_received = yield from csocket_bob.recv()  # Recibo los bits de Alice
        for i in range(n):
            if nums_to_del[i] != nums_received[i]:
                print(f"Alert! Possible eavesdropping detected at bit {i}!")
                errors+=1
        print(f"QBER detected by {self.NODE_NAME}: {errors/n*100}%")
        return {}


class BobProgram(Program):
    NODE_NAME = "Bob"
    PEER_ALICE = "Alice"

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name=f"program_{self.NODE_NAME}",
            csockets=[self.PEER_ALICE],
            epr_sockets=[self.PEER_ALICE],
            max_qubits=2,
        )

    def run(self, context: ProgramContext):
        # get classical sockets
        csocket_alice = context.csockets[self.PEER_ALICE]
        # get EPR sockets
        epr_socket_alice = context.epr_sockets[self.PEER_ALICE]
        # get connection to QNPU
        connection = context.connection

        print(f"{ns.sim_time()} ns: Hello from {self.NODE_NAME}")
        results = []
        bases = []

        for i in range(100):

            epr_qubit = epr_socket_alice.recv_keep()[0] # Recibo el par de Alice
            if random.randint(0, 1) == 1:
                epr_qubit.H()  # Aplico una puerta X 
                base = 'X'
            else:    
                base = 'Z'
            result = epr_qubit.measure()  # Mido el qubit

            yield from connection.flush() # Mando las intrucciones al Quantum Network Processor Unit
            results.append(int(result)) 
            bases.append(base)
   
        bases_alice = yield from csocket_alice.recv()  # Recibo los resultados de Alice
        csocket_alice.send(bases) # Mando mis resultados a Alice
        # print(f"{ns.sim_time()} ns: Bases from Alice: {bases_alice}")

        raw_key = []
        for i in range(100):
            if bases_alice[i] == bases[i]:
                raw_key.append(results[i])
        
        errors = 0

        nums_to_del = raw_key[::2]
        n = len(nums_to_del)
        csocket_alice.send(nums_to_del) # Mando la mitad de los bits a Alice
        nums_received = yield from csocket_alice.recv()  # Recibo los bits de Alice
        for i in range(n):
            if nums_to_del[i] != nums_received[i]:
                print(f"Alert! Possible eavesdropping detected at bit {i}!")
                errors+=1
        print(f"QBER detected by {self.NODE_NAME}: {errors/n*100}%")


        print(f"{ns.sim_time()} ns: Raw key established by {self.NODE_NAME}: {raw_key}")
        return {}
