# Steering voice button: short press for Siri

For the Indian 2024 diesel Creta with product SU2IFL.IND.0000.V010.001.260430 and HMG-API base 1.0.1.2. The owner confirmed that holding the wheel voice button opens Siri with CarPlay connected. This separate mod gives a tap the existing voice-hold action. Physical holds continue through the normal handler. The tap mapping also applies with CarPlay disconnected, when the head unit decides what a voice hold does.

1. With the car parked, connect the iPhone to CarPlay and insert the USB. In Nemesis → Package Store → USB, install **Creta steering voice (short press) 1.0.0**.
2. After install success, remove the drive and tap and release the steering-wheel voice button once. Ask Siri “What time is it?” If installation fails, record the message. If HMG-API requests a restart, allow the unit at least two minutes after startup before restarting.
3. Dismiss Siri, then try the physical hold that worked before. If the short press opens Hyundai voice or does nothing, report that result before changing settings.

To revert, uninstall **Creta steering voice (short press)** from Nemesis → My Packages. The installer applies the binding and removal withdraws it. Both were exercised on a host fixture alongside the stage 17 wireless mod. Physical tap and hold after installation still require owner verification.

## Build

The package contains one input declaration adapted from the upstream Car Check example. The installed 1.0.1 runtime reads the sent key and injects a voice hold using the physical input device. The diesel framework identifies the steering PTT key as 0x108. The HMG-API engine host publishes one replacement binding, rejects the tested alternate firmware products, and restores the previous input list on removal. System hashes and wireless settings matched the stage 17 fixture before and after installation.

Run build.py with --baseline pointing to the signed original stage 08 wireless wrapper, --engine-classes pointing to the compiled signing engine, --key pointing to your local owner key, and --output pointing to a new ZIP. Use JDK 17. The baseline supplies the generic Nemesis package lifecycle scripts. The signed payload contains mod.json and its signature metadata.
