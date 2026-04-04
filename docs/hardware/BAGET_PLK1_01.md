# БАГЕТ-ПЛК1-01 — Getting Started

**Источник:** BAGET-PLK1-01_getting_started_v_2_3-1.pdf  
**Авторы:** Мощевикин А.П., Голяков М.А.  
**Дата:** 17.03.2025

## Обзор

Одноплатный микрокомпьютер **БАГЕТ-ПЛК1-01** построен на микроконтроллере **Комдив-МК (К5500ВК018)**, разработанном в НИИСИ РАН.

### Аппаратные ресурсы

| Компонент | Объём | Примечание |
|-----------|-------|-----------|
| Встроенное ПЗУ МК | 16 кБ | В микроконтроллере Комдив-МК |
| Встроенное ОЗУ МК | 512 кБ | В микроконтроллере Комдив-МК |
| Внешнее ОЗУ DDR3 | 512 МБ | На плате |
| Системное Flash-ПЗУ (D30, W25Q32, QSPI) | 4 МБ | Загрузчик barebox или ПО пользователя |
| Пользовательское Flash-ПЗУ (D31, W25Q32, SPI0) | 4 МБ | Flash-память |
| Пользовательское EEPROM (D8, M24C32, I2C0) | 4 кБ | |
| SD-карта | 32 ГБ | Образ ОС Debian |

### Интерфейсы

- **USB** — через FTDI FT2232HL (два конвертера: A — JTAG/загрузка, B — консоль)
- **Ethernet** — разъём X3 (RJ45), DHCP по умолчанию
- **Питание** — 7–18 В через коаксиальный разъём X7 (не только USB!)
- **Консоль** — 115200, 8N1

## Режимы работы

Определяются перемычками **SA4**, **SA9**.

### Режим 1 — Debian (с ОС)
- SA4: положение 1-2 (EXT RAM)
- SA9: OFF
- Загрузка ОС Debian с SD-карты
- Используется внешнее ОЗУ 512 МБ и внешнее ПЗУ
- Полный набор средств Debian (Python, утилиты, пакеты)
- Совместимость с экосистемой Raspberry Pi
- Перемычки SA4–SA7: все в левое положение (Ethernet, EXT ROM, EXT RAM, LITTLE ENDIAN)

### Режим 2 — Baremetal (без ОС)
- SA4: положение 2-3 (INT RAM)
- SA9: ON
- Код исполняется из внешнего системного ПЗУ
- Только встроенное ОЗУ 512 кБ
- Разработка: стиль Arduino (setup/loop) или стандартный Си
- Перемычки: SA5–SA7 в левое, SA4 в правое (INT RAM)

## Подключение к компьютеру (Windows)

### Драйверы
- При появлении неизвестного устройства — установить FTDI FT2232HL VCP driver
- Скачать: https://ftdichip.com/drivers/vcp-drivers/
- После установки: два USB Serial Converter (A и B) + один-два COM-порта
- Если виден только один COM-порт — активировать VCP в свойствах каждого конвертера (вкладка «Дополнительно» → «Загрузить VCP»)

### Терминал
- Рекомендуется **TeraTerm**: https://github.com/TeraTermProject/teraterm/releases/download/v5.3/teraterm-5.3.exe
- Параметры: 115200, 8, none, 1, none
- Подключение через **USB-конвертер B** (консоль)

### Проверка работы (Debian)
1. Перемычки в режим 1
2. Подать питание 7–18 В через X7
3. Подключить USB
4. Открыть TeraTerm на COM-порт конвертера B
5. Нажать RESET → замигает светодиод RX0 → диагностические сообщения → приглашение bash
6. Логин root / sudo

## Среда разработки Baremetal (Windows 10 + WSL)

### Установка

1. **Включить виртуализацию** Intel VT в BIOS
2. **Установить VS Code**: https://code.visualstudio.com/download
3. **Включить Hyper-V и WSL** (Панель управления → Компоненты Windows)
4. **Установить Windows Terminal** из Microsoft Store
5. **Установить usbipd** для проброса USB в WSL:
   ```
   winget install --interactive --exact dorssel.usbipd-win
   ```
6. **Установить WSL 2**:
   ```powershell
   wsl.exe --update
   wsl --set-default-version 2
   ```
7. **Установить Debian**:
   ```powershell
   wsl --install --distribution Debian
   ```
   После установки: `wsl -d Debian`, создать пользователя, обновить:
   ```bash
   sudo apt update && sudo apt upgrade
   ```

### Проброс USB в WSL

```powershell
# Список USB-устройств (от администратора)
usbipd list
# Найти BUSID для USB Serial Converter A, B
usbipd bind --busid <BUSID>    # однократно
usbipd attach --wsl --busid <BUSID>  # после каждой перезагрузки
```

### Установка flashrom (программатор ПЗУ)

```bash
# В Debian WSL
tar -xf kmk_flashrom.tar
sudo apt install libpci-dev libgusb-dev libftdi1-dev
sudo apt install make gcc g++ vim mc screen
cd flashrom
make
sudo make install
```

### Сохранение/загрузка образа ПЗУ

```bash
# Сохранить (бэкап barebox)
sudo flashrom -p ft2232_spi:type=kmk -c W25Q32BV/W25Q32CV/W25Q32DV -r ~/barebox_299.bin

# Загрузить
sudo flashrom -p ft2232_spi:type=kmk -c W25Q32BV/W25Q32CV/W25Q32DV -w ~/barebox_299.bin
```

### Компиляция и прошивка программы

```bash
# Установить кросс-компиляторы
sudo apt install gcc-mips-linux-gnu g++-mips-linux-gnu

# Распаковать ППП МК
tar -xf 20250226_pppmk.tar.bz2
# Результат: ~/arduino/ (проекты Arduino-стиля), ~/psp_mc/ (проекты на Си)

# Открыть в VS Code
cd arduino/
code .

# Скомпилировать пример
cd apps/i2c_scanner
make
# Результат: ram.bin, ram.dis, ram.elf
```

### Скрипт прошивки (kmk.sh)

Создать `kmk.sh` в каталоге проекта:
```bash
#!/bin/sh
BAREBOXIMG=$1
if [ ! -e "$BAREBOXIMG" ]; then
  echo "usage: $0 <barebox-image>"
  exit 1
fi
cat > /tmp/layout <<EOF
00000000:0007ffff barebox
EOF
dd if=/dev/zero ibs=1M count=4 | tr "\000" "\377" > /tmp/padded.img
dd if=$BAREBOXIMG of=/tmp/padded.img conv=notrunc
flashrom -p ft2232_spi:type=kmk -c W25Q32BV/W25Q32CV/W25Q32DV -w /tmp/padded.img
```

```bash
chmod +x kmk.sh
make && sudo ./kmk.sh ram.bin
```

### Просмотр вывода программы

**Вариант 1 — TeraTerm (Windows):**
```powershell
usbipd detach --busid <BUSID>  # вернуть USB в Windows
```
Открыть TeraTerm на COM-порт конвертера B.

**Вариант 2 — minicom (Debian WSL):**
```bash
sudo apt install minicom
sudo minicom -D /dev/ttyUSB1
# Параметры: 115200 8N1
# Выход: Ctrl-A + Q
```

## Ключевые компоненты ПО

| Компонент | Назначение |
|-----------|-----------|
| **ППП МК** (НИИСИ РАН) | Пакет поддержки программирования Комдив-МК |
| **barebox** | Загрузчик ОС Debian с SD-карты |
| **kmk_flashrom** | Программатор ПЗУ (модифицированный flashrom) |
| **usbipd-win** | Проброс USB из Windows в WSL |
| **VS Code + WSL** | IDE для разработки |
| **gcc-mips-linux-gnu** | Кросс-компилятор для Комдив-МК (MIPS) |

## Важные замечания

- ⚠️ **Питание** — обязательно через разъём X7 (7–18 В), не только USB
- ⚠️ **Перемычки** — переключать только при выключенном питании
- ⚠️ **SD-карта** — перед экспериментами сделать бэкап образа
- ⚠️ **MAC-адрес** — генерируется случайно, IP по DHCP может меняться
- ⚠️ **USB-кабель** — использовать качественный, подключать к разъёму на материнской плате
- ⚠️ **usbipd bind** — однократно, **usbipd attach** — после каждой перезагрузки
