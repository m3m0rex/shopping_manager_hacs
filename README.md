# Shopping Manager (HACS Integration)

Home-Assistant-Integration für die [Shopping-Manager-App](https://github.com/m3m0rex/shopping_manager).
Spiegelt deine Einkaufslisten als `todo.*`-Entitäten nach Home Assistant und bietet
Services zum Anlegen/Umbenennen/Löschen von Listen.

## Installation (HACS)

1. HACS → **Integrationen** → ⋮ → **Benutzerdefiniertes Repository hinzufügen**
   - URL: `https://github.com/m3m0rex/shopping_manager_hacs`
   - Kategorie: **Integration**
2. HACS → **Integrationen** → **Shopping Manager** installieren
3. **Einstellungen → Geräte & Dienste → + Integration** → **Shopping Manager**
   - **Host:** URL deiner Shopping-Manager-App (z. B. `https://deine-domain.de`)
   - **Token:** Benutzer-Token aus der App (Einstellungen → Integrationen → "Token erzeugen")

## Was die Integration macht

- Erstellt pro Backend-Liste eine `todo.shopping_manager_<...>`-Entity in HA
- Aktualisiert die Artikel regelmäßig (Scan-Intervall in der Config)
- Meldet `entity_id ↔ list_id` ans Backend (`/api/ha/mapping`), damit die App
  die HA-Liste der richtigen Backend-Liste zuordnen kann
- Services zum Verwalten von Listen (siehe unten)

## Services

| Service | Felder | Zweck |
|---------|--------|-------|
| `shopping_manager.create_list` | `name` | Neue Liste anlegen |
| `shopping_manager.rename_list` | `list_id`, `name` | Liste umbenennen |
| `shopping_manager.delete_list` | `list_id` | Liste löschen |

Beispiel (Entwicklerwerkzeuge → Dienste):

```yaml
service: shopping_manager.create_list
data:
  name: Wocheneinkauf
```

## Zwei-Wege-Sync mit der App

- **App → HA:** Änderungen in der App landen im Backend; diese Integration liest sie
  und spiegelt sie in die `todo.*`-Entities.
- **HA → App:** Beschreibbare HA-Listen (z. B. *Local To-Do* Integration) können direkt
  aus der App bearbeitet werden; reine `shopping_manager_*`-Spiegel sind read-only
  und werden aus dem Backend gespeichert.

## Troubleshooting

- **Listen fehlen in HA:** Integration neu laden (Einstellungen → ⋮ → "Neu laden") oder
  Scan-Intervall verkürzen.
- **401 / Verbindung fehlgeschlagen:** Token in der App erneuern und in der
  Integration erneut eintragen.
- **Logs:** HA → Einstellungen → Protokolle → nach `shopping_manager` filtern.

## Versionierung

`manifest.json` `version` MUSS mit einem getaggten GitHub-Release übereinstimmen
(HACS lehnt nur einen Commit-Hash ab). Releases: siehe
https://github.com/m3m0rex/shopping_manager_hacs/releases
