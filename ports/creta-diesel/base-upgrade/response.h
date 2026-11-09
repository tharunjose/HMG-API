/* Strict incremental reply validator for the read-only vehicle protocol.
 * Inspired by Creta d1f3290's completion fix. Missing, reordered, oversized,
 * truncated or extra lines fail; no output is published until all names match.
 */
#define VEHICLE_REPLY_MAX 16384
struct vehicle_reply { char data[VEHICLE_REPLY_MAX]; unsigned used, line; int next, bad; };
static void vehicle_reply_init(struct vehicle_reply *r) {
    r->used = r->line = 0; r->next = 1; r->bad = 0;
}
static int vehicle_reply_feed(struct vehicle_reply *r, const char *p, unsigned n, int argc, char **argv) {
    unsigned i, j;
    if (r->bad || n >= VEHICLE_REPLY_MAX - r->used) { r->bad=1; return -1; }
    for (i=0; i<n; i++) {
        char c=p[i];
        if (r->next >= argc || c=='\0' || c=='\r') { r->bad=1; return -1; }
        r->data[r->used++]=c;
        if (c!='\n') continue;
        for (j=0; argv[r->next][j]; j++)
            if (r->line+j >= r->used-1 || r->data[r->line+j]!=argv[r->next][j]) { r->bad=1; return -1; }
        if (r->line+j+2 >= r->used || r->data[r->line+j]!=' ') { r->bad=1; return -1; }
        r->next++; r->line=r->used;
    }
    return r->next==argc ? 1 : 0;
}
