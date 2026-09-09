# Shopping Manager – HACS Integration

Home Assistant Custom Integration für den [Shopping Manager](https://github.com/m3m0rex/shopping_manager).
Dieses Repo enthält **nur** die HA-Integration (HACS-tauglich).

## Installation über HACS (einfachste Methode)

1. HACS öffnen → Kategorie **Integrationen**
2. Oben rechts auf die drei Punkte → **Benutzerdefiniertes Repository**
3. Repository-URL: `https://github.com/m3m0rex/shopping_manager_hacs`
4. Kategorie: **Integration** → Hinzufügen
5. Im HACS-Store „Shopping Manager" suchen und installieren
6. Home Assistant **neu starten**
7. *Einstellungen → Geräte & Dienste → Integration hinzufügen → Shopping Manager*
8. Host-URL eingeben (z.B. `http://localhost:3000` bzw. IP deines Servers)
   – Falls im Backend `API_TOKEN` gesetzt ist, hier ebenfalls eintragen
9. Fertig: du hast
   - 3 Sensoren: `sensor.shopping_manager_offen`, `_abgehakt`, `_gesamt`
   - Eine native **Todo-Liste** `todo.shopping_manager_einkaufsliste`
   - Zwei Services: `shopping_manager.add_item` und `shopping_manager.toggle_checked`

## Variante B: Manuell (ohne HACS)

Kopiere den Ordner `custom_components/shopping_manager/` nach
`<HA_CONFIG>/custom_components/shopping_manager/` und starte HA neu.
Danach wie oben unter Schritt 7–9 fortfahren.

## Services nutzen (Beispiel Automatisierung)

```yaml
service: shopping_manager.add_item
data:
  name: "Milch"
  quantity: "2 l"
```

## Todo-Liste im Dashboard

Füge eine **Todo-Liste**-Karte hinzu und wähle
`Einkaufsliste (Shopping Manager)`. Artikel können direkt abgehakt werden
und erscheinen live in der App.

Siehe auch `configuration.yaml.example` für REST-Sensor / Webhook-Variante.
