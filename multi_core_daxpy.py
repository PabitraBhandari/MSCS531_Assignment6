import os
import m5
from m5.objects import *

# Create the system we are going to simulate
system = System()

# Set the clock frequency of the system
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "2GHz"
system.clk_domain.voltage_domain = VoltageDomain()

# Set up the system's memory mode and range
system.mem_mode = "timing"  # Use timing accesses
system.mem_ranges = [AddrRange("256MB")]  # Memory size

# The number of CPU cores
num_cores = 4
system.cpu = [TimingSimpleCPU() for _ in range(num_cores)]

system.membus = SystemXBar()

# Connect the CPU ports to the memory bus
for i, cpu in enumerate(system.cpu):
    cpu.icache_port = system.membus.cpu_side_ports
    cpu.dcache_port = system.membus.cpu_side_ports
    cpu.createInterruptController()

    # For X86 CPUs, connect interrupts directly to the memory bus
    cpu.interrupts[0].pio = system.membus.mem_side_ports
    cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
    cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Create a DDR3 memory controller and connect it to the memory bus
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Connect the system port to the memory bus
system.system_port = system.membus.cpu_side_ports

# Set the path for the daxpy binary
binary = '/Users/cristbhandari/gem5/configs/sample3/daxpy_kernel'

# Check if the binary exists
if not os.path.exists(binary):
    raise FileNotFoundError(f"Binary not found at {binary}")

# Initialize the workload
system.workload = SEWorkload.init_compatible(binary)

# Assign the daxpy process to each core
for i, cpu in enumerate(system.cpu):
    process = Process()
    process.cmd = [binary, str(i)]  # Pass thread ID as argument
    process.pid = 100 + i  # Assign unique PID
    cpu.workload = [process]  # Assign process to the CPU workload vector
    cpu.createThreads()

# Set up the root SimObject and instantiate all objects
root = Root(full_system=False, system=system)
m5.instantiate()

print(f"Starting the simulation with {num_cores} core(s)!")
exit_event = m5.simulate(2 * 10**9)  # Limit to 2 billion ticks for testing
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
