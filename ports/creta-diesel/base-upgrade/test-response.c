#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "response.h"
int main(void) {
    struct vehicle_reply r;
    char *a[]={"vehicle","battery12v.soc","gear.park"};
    const char *good="battery12v.soc 79\ngear.park 1\n";
    unsigned cut, n=(unsigned)strlen(good);
    for(cut=0;cut<=n;cut++) {
        vehicle_reply_init(&r);
        int first=vehicle_reply_feed(&r,good,cut,3,a);
        assert(first==(cut==n?1:0));
        assert(vehicle_reply_feed(&r,good+cut,n-cut,3,a)==1);
        assert(r.used==n && !memcmp(r.data,good,n));
    }
    const char *bad[]={"battery12v.soc \ngear.park 1\n","gear.park 1\nbattery12v.soc 79\n",
        "battery12v.soc 79\nbattery12v.soc 80\n","battery12v.soc 79\ngear.park 1\nextra 1\n",
        "battery12v.socx 79\ngear.park 1\n","battery12v.soc 79\r\ngear.park 1\n"};
    for(unsigned i=0;i<sizeof(bad)/sizeof(bad[0]);i++) {
        vehicle_reply_init(&r); assert(vehicle_reply_feed(&r,bad[i],strlen(bad[i]),3,a)==-1);
    }
    const char *partial[]={"","battery12v.soc 79","battery12v.soc 79\n","battery12v.soc 79\ngear.park 1"};
    for(unsigned i=0;i<sizeof(partial)/sizeof(partial[0]);i++) {
        vehicle_reply_init(&r); assert(vehicle_reply_feed(&r,partial[i],strlen(partial[i]),3,a)==0);
    }
    vehicle_reply_init(&r); assert(vehicle_reply_feed(&r,"battery12v.soc -\n",strlen("battery12v.soc -\n"),2,a)==1);
    vehicle_reply_init(&r); assert(vehicle_reply_feed(&r,"\0",1,2,a)==-1);
    char huge[VEHICLE_REPLY_MAX]; memset(huge,'x',sizeof(huge));
    vehicle_reply_init(&r); assert(vehicle_reply_feed(&r,huge,sizeof(huge),2,a)==-1);
    puts("PASS: every split boundary; wrong/repeated/extra names; empty/truncated replies; sentinel; overflow");
}
