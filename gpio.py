from pynq import Overlay, Interrupt, GPIO
import asyncio

overlay = Overlay("design_2.bit")
button_gpio = overlay.axi_gpio_1
interrupt = Interrupt("axi_gpio_1/ip2intc_irpt")

led = overlay.axi_gpio_0
led.register_map.GPIO_TRI = 0x0

gpio = overlay.ip_dict['axi_gpio_1']
btn = AxiGPIO(gpio).chanel0

button_gpio.register_map.GPIO_TRI = 0xF
button_gpio.register_map.GIER = 0x80000000  # Enable global interrupts
button_gpio.register_map.IP_IER = 0x1  # Enable interrupt for Channel 1
button_gpio.register_map.IP_ISR = 0x1  # Clear any existing interrupt

print("System initialized and waiting for GPIO signal...")

async def process_button_signal():
    print("GPIO signal detected!")
    button_state = int(button_gpio.register_map.GPIO_DATA) & 0x1

    if button_state == 1:
        print("Inside if:", button_state)
        led.register_map.GPIO_DATA = 0x1
    else:
        print("Inside else:", button_state)
        led.register_map.GPIO_DATA = 0x0

    print(f"button state: {bin(button_state)}")

    button_gpio.register_map.IP_ISR = 0x1
    print("Process complete. Waiting for next signal.")

async def handle_interrupt():
    """Handles the GPIO interrupt."""
    await btn.wait_for_intrrupt_async()
    #await interrupt.wait()  # Wait for the GPIO interrupt
    await process_button_signal()
    await handle_interrupt()
async def main():
    try:
        await handle_interrupt()
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")
    finally:
        button_gpio.register_map.GIER = 0x0  # Disable global interrupts
        button_gpio.register_map.IP_IER = 0x0  # Disable individual interrupt
        interrupt.clear()
        print("Cleanup done. Exiting program.")

asyncio.run(main())
