# Steering phone button opens CarPlay Phone

Owner-confirmed on 6 November 2026 — a short steering phone-button press opens CarPlay Phone with creta-carplay-phone 1.0.0 installed. Incoming-call answering with the button remains to be checked.

For SU2IFL.IND.0000.V010.001.260430. Owner confirmed the native activity opens CarPlay Phone using CarPlayMode 2. This standalone mod observes short wheel Call releases and requests that activity if CarPlay is connected and its call status, mode and Android telephony all indicate idle.

1. While parked with CarPlay connected, insert the USB. In Nemesis → Package Store → USB, install **Creta CarPlay Phone button 1.0.0**.
2. After success remove USB. Once Android has run for at least two minutes, use HMG-API → Restart unit. Reconnect wireless CarPlay.
3. Show Music or Maps in CarPlay and briefly press the steering phone button. Report whether Phone opens. At the next normal incoming call, verify answering from the wheel works.

To revert, uninstall only **Creta CarPlay Phone button** in Nemesis → My Packages and restart the unit. The previous button configuration returns. Install and removal passed on the host fixture with the stage17 wireless and stage20 Siri mods. The owner confirmed the installed handler opens CarPlay Phone. Incoming-call answering is pending.

## Implementation and checks

The mod observes WindowManagerService.interceptKey through the already-mapped automotive loader. It tracks a matching physical down/up from one device, excludes repeats, cancelled events and holds of 500 ms or more, then posts the activity request. It checks idle again at dispatch. The native DiPO manager distinguishes ringing 1 and off-hook 2 from idle 0. An unavailable check prevents a launch.

Build using build.py with the same inputs as ../short-press-siri/build.py plus --android-jar and --r8. Use an absolute JDK17 --java path. The compile-only API stubs are excluded from the DEX, which was disassembled to verify the four PhoneKey classes. Compile PhoneKeyTest with PhoneKey.java, the API stubs and Android jar, then run with assertions to exercise tap, duplicate, call-state transitions, repeat, hold and cancellation handling. The host engine install/apply/remove test retained the existing Siri input binding, projection settings and system file hashes. Actual vehicle call handling is pending.
