import netsquid as ns
import numpy as np

from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta

def xor(a,b):
    c=[]
    for i in range(len(a)):
        if a[i]==b[i]:
            c.append(0)
        else:
            c.append(1)
    return c

def AND(x,y):
    z=[]
    for i in range(len(x)):
        if x[i]==1 and y[i]==1:
            z.append(1)
        else:
            z.append(0)
    return z

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
        n=10000
        x=np.random.randint(0,2,size=n)
        a=[]
        for i in range(n):
            epr_qubit = epr_socket_bob.create_keep()[0]
            if x[i]==0:
                result=epr_qubit.measure()
            else:
                epr_qubit.rot_Y(1,1)
                result=epr_qubit.measure()
            yield from connection.flush()
            a.append(int(result))
        
        csocket_bob.send(a)
        csocket_bob.send(x)
        # print(f'String de Alice={x}')
        # print(f'String a={a}')
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
        

        n=10000
        y=np.random.randint(0,2,size=n)
        b=[]
        for i in range(n):
            epr_qubit = epr_socket_alice.recv_keep()[0]
            if y[i]==0:
                epr_qubit.rot_Y(1,2)
                result=epr_qubit.measure()
            else:
                epr_qubit.rot_Y(7,2)
                result=epr_qubit.measure()
            yield from connection.flush()
            b.append(int(result))

        a=yield from csocket_alice.recv()
        x=yield from csocket_alice.recv()

        a_b=xor(a,b)
        x_y=AND(x,y)
        total=0
        for i in range(n):
            if a_b[i]==x_y[i]:
                total+=1
        
        # print(f'String b={b}')
        print(f'Porcentaje de victoria:{total/n*100}')

        
        # print(f'String de Bob={y}')
        return {}
