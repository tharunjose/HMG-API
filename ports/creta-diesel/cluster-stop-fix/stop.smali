.method stop()V
    .registers 12

    invoke-virtual {p0}, Lhmgapi/mods/wireless/dipo/CpTurns;->hudBlank()V
    iget-boolean v0, p0, Lhmgapi/mods/wireless/dipo/CpTurns;->guiding:Z
    if-eqz v0, :done
    iget-object v0, p0, Lhmgapi/mods/wireless/dipo/CpTurns;->display:Lhmgapi/mods/wireless/api/TurnDisplay;
    if-eqz v0, :generic
    invoke-interface {v0}, Lhmgapi/mods/wireless/api/TurnDisplay;->guidanceEnded()V
    goto :done

    :generic
    iget-object v0, p0, Lhmgapi/mods/wireless/dipo/CpTurns;->cluster:Lhmgapi/hook/Cluster;
    const/4 v1, 0x0
    const/4 v2, 0x0
    const/4 v3, 0x0
    const/4 v4, 0x0
    const/4 v5, -0x1
    const/4 v6, 0x0
    const/4 v7, 0x0
    const/4 v8, 0x0
    const/4 v9, -0x1
    invoke-virtual/range {v0 .. v9}, Lhmgapi/hook/Cluster;->tbtInfo(IIFFIIIII)V

    :done
    const/4 v0, 0x0
    iput-boolean v0, p0, Lhmgapi/mods/wireless/dipo/CpTurns;->guiding:Z
    iput-object v0, p0, Lhmgapi/mods/wireless/dipo/CpTurns;->mainOwner:Ljava/lang/Integer;
    return-void
.end method
