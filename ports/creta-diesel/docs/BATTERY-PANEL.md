# Creta 12V battery panel trial

This tap-to-refresh split-screen widget requests the 12V battery state of charge reported by the head unit. A missing reading displays **Unavailable**. A successful reading shows the time of the request. HMG-API can cache this signal for up to 30 seconds. The widget asks for one vehicle reading, has no background polling or steering-wheel binding, and declares no vehicle commands.

The trial is based on [VysseCodes’ Side Panel example](https://github.com/VysseCodes/HMG-API/tree/main/mods/examples/side-panel) and targets the Indian diesel product `SU2IFL.IND.0000.V010.001.260430` with HMG-API 1.0.1 or later. On-car rendering and a valid diesel charge reading still require a parked check.

1. In NEMESIS → Package Store → USB, select **Creta 12V battery panel**. Follow any HMG-API restart prompt.
2. Open the split-screen settings and enable HMG-API’s page. Open the split-screen panel, select **12V battery** and tap the widget. Record the percentage or “Unavailable”. The page can be refreshed without the USB connected.
3. To remove it, uninstall **Creta 12V battery panel** through NEMESIS → My Packages. The separate USB battery logger has its own package and purpose.

The app and mod sources are in [mods/creta-diesel-battery-panel](../../../mods/creta-diesel-battery-panel). They follow the upstream mod-app build layout. A private trial build used an Android 4.4 API 19 platform, Android Build Tools 34.0.0, a v1-signed widget APK and the existing diesel mod signer. Keep the APK signing identity for later updates. The public source tree contains no signing material.

The installed-base host fixture accepted this trial alongside the official NEMESIS menu shortcut and the wireless mod, published the widget registration, simulated APK installation and removal, and rejected the EV product for the diesel widget. Physical head-unit behavior is still open.
