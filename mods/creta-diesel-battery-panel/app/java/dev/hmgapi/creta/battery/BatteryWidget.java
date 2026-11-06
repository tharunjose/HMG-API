package dev.hmgapi.creta.battery;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.text.format.DateFormat;
import android.widget.RemoteViews;

import hmgapi.client.HmgApi;

import java.io.IOException;
import java.util.Date;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Diesel variant of VysseCodes' Side Panel example. Read only, refreshed on tap. */
public class BatteryWidget extends AppWidgetProvider {
    private static final String REFRESH = "dev.hmgapi.creta.battery.REFRESH";
    private static final ExecutorService READS = Executors.newSingleThreadExecutor();

    @Override
    public void onReceive(Context context, Intent intent) {
        String action = intent.getAction();
        if (!REFRESH.equals(action) && !AppWidgetManager.ACTION_APPWIDGET_UPDATE.equals(action)) {
            super.onReceive(context, intent);
            return;
        }
        final Context app = context.getApplicationContext();
        final PendingResult pending = goAsync();
        READS.execute(new Runnable() {
            @Override public void run() {
                try {
                    refresh(app);
                } finally {
                    pending.finish();
                }
            }
        });
    }

    private static void refresh(Context app) {
        String reading = "Unavailable";
        String detail = "Tap to retry";
        try {
            String value = HmgApi.connect().timeout(2000).vehicle("battery12v.soc").get("battery12v.soc");
            if (value != null && !value.equals("-")) {
                double percent = Double.parseDouble(value);
                if (percent >= 0 && percent <= 100) {
                    reading = value + "%";
                    detail = "Read at " + DateFormat.getTimeFormat(app).format(new Date()) + " · Tap to refresh";
                }
            }
        } catch (IOException | NumberFormatException ignored) {
            // A failed read must replace the prior value rather than presenting stale charge.
        }
        RemoteViews view = new RemoteViews(app.getPackageName(), R.layout.battery);
        view.setTextViewText(R.id.reading, reading);
        view.setTextViewText(R.id.detail, detail);
        Intent refresh = new Intent(app, BatteryWidget.class).setAction(REFRESH);
        view.setOnClickPendingIntent(R.id.root, PendingIntent.getBroadcast(app, 0, refresh, PendingIntent.FLAG_UPDATE_CURRENT));
        AppWidgetManager.getInstance(app).updateAppWidget(new ComponentName(app, BatteryWidget.class), view);
    }
}
