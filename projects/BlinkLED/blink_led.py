import lgpio
import time
import signal
import sys

# Using lgpio for better compatibility on Ubuntu 24.04
# GPIO 16 (BCM)
LED_PIN = 16

def cleanup_and_exit(chip, pin):
    print("\nCleaning up and exiting...")
    try:
        lgpio.gpio_write(chip, pin, 0)
        lgpio.gpiochip_close(chip)
    except:
        pass
    sys.exit(0)

def main():
    try:
        # Open the gpiochip (usually 0 or 4 on RPi, Ubuntu mapping varies)
        # We'll try the default chip first.
        chip = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_output(chip, LED_PIN)
        
        print(f"Blinking LED on GPIO {LED_PIN} (BCM) via lgpio. Press Ctrl+C to stop.")
        
        # Setup signal handler for clean exit
        signal.signal(signal.SIGINT, lambda sig, frame: cleanup_and_exit(chip, LED_PIN))

        while True:
            lgpio.gpio_write(chip, LED_PIN, 1)
            time.sleep(0.5)
            lgpio.gpio_write(chip, LED_PIN, 0)
            time.sleep(0.5)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
