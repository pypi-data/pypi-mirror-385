# OTDR .sor reader/converter

CLI per convertire file `.sor` da strumenti OTDR in `.json` o plot `.html`.

## Installazione

Per installare il pacchetto, da terminale nella cartella che contiene il file wheel:

```cmd
pip install \otdr_reader-0.2.8-py3-none-any.whl
```

modificando opportunamente la versione nel nome del file.

Attenzione che, per qualche motivo, non sempre funziona da PowerShell mentre sembra funzionare normalmente da command prompt.

Opzionalmente, da terminale PowerShell:

```cmd
otdr_reader --install-completion
```

## Command line interface

I comandi disponibili da command prompt sono:

* `otdr-reader file`
* `otdr-reader folder`

Di seguito le descrizioni dei singoli comandi.

### `otdr-reader file`

**Utilizzo**:

```console
$ otdr-reader [OPTIONS] FILE
```

**Argomenti**:

* `FILE`: [required]

**Opzioni**:

* `--output TEXT`. Default: `html`. Valori ammessi: `html`, `json`.
* `--smooth INT`. Default: `0`. Numero di campioni per la finestra della media mobile. Utilizzato solo per il plot.
* `--logo / --no-logo`. Default: `--logo`. Aggiunge logo Cohaerentia nel grafico.

**Descrizione**:

Comando per convertire un file `.sor` di un OTDR in un plot html o un file json. Il file verrà creato con stesso nome del `.sor` e nella stessa cartella.

### `otdr-reader folder`

**Utilizzo**:

```console
$ otdr-reader convert-folder [OPTIONS]
```

**Opzioni**:

* `--folder TEXT`. Default: current folder.
* `--output TEXT`. Default: `html`. Valori ammessi: `html`, `json`.
* `--target-folder TEXT`. Default: sottocartella `converted`.
* `--target-filename TEXT`
* `--smooth INT`. Default: `0`. Numero di campioni per la finestra della media mobile. Utilizzato solo per il plot.
* `--logo / --no-logo`. Default: `--logo`. Aggiunge logo Cohaerentia nel grafico.

**Descrizione**:

Comando per convertire tutti i files `.sor` di un OTDR contenuti nella cartella `FOLDER`. Possono essere convertiti in files `json` (un file per ogni `.sor`) o in un singolo plot html.
