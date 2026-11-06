package hmgapi.mods.creta;

/** Physical RHD seat names mapped to the native API labels confirmed on this car. */
enum SeatTarget {
    DRIVER("right driver", "startup_enabled", "level", true, "ast", "passenger"),
    PASSENGER("left passenger", "passenger_enabled", "passenger_level", false, "drv", "driver");

    final String name, enabledKey, levelKey, readPoint, writePoint;
    final boolean defaultEnabled;

    SeatTarget(String name, String enabledKey, String levelKey, boolean enabled,
               String nativeReadSeat, String nativeWriteSeat) {
        this.name = name;
        this.enabledKey = enabledKey;
        this.levelKey = levelKey;
        this.defaultEnabled = enabled;
        readPoint = "framework.bcm_service." + nativeReadSeat + "_seat_heat_state";
        writePoint = "framework.usm_service.seat_heat_" + nativeWriteSeat;
    }
}
