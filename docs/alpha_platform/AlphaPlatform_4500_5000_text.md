=== Page 1 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
Обратите внимание, что логин и пароль администратора LDAP нужно указывать в конфигурационном файле
агента безопасности, подробнее об этом – в разделе 4. Агент безопасности и его настройка (стр. 64),
подраздел Указать администратора LDAP (стр. 65).
3.2.3. Резервирование LDAP-сервера
Резервирование (репликация) LDAP-сервера позволяет синхронизировать конфигурации двух и более
серверов. Резервирование может быть:
однонаправленным – в этом случае конфигурация одного сервера (поставщика) тиражируется на
другие сервера (приемники);
разнонаправленным – в этом случае синхронизируются конфигурации нескольких серверов.
3.2.3.1. Однонаправленное резервирование
Прежде чем перейти к настройкам резервирования:
1. Убедитесь, что типы баз данных всех серверов – «mdb», с помощью команды:
sudo slapcat -n0
Пример искомого значения: «dn: olcDatabase={1}mdb,cn=config». Если тип БД отличается, то во всех
файлах, создаваемых и применяемых в инструкции ниже, следует указывать правильный тип базы.
2. Сделайте бэкап конфигурации и БД сервера-поставщика в текущей папке с помощью команды:
cd /opt/Automiq/Alpha.Security
sudo sh ./openldap-conf-and-data-backup.sh
Для восстановления конфигурации и БД OpenLDAP в случае ошибок резервирования, выполните
команды:
cd /opt/Automiq/Alpha.Security
sudo sh ./openldap-conf-and-data-restore.sh
22
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 2 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
Чтобы настроить однонаправленное резервирование:
1. Определите, какой из LDAP-серверов будет поставщиком, а какие – приемниками.
2. Настройте сервера-приемники:
ОБРАТИТЕ ВНИМАНИЕ
Описанные в пункте действия выполните на каждом из серверов-приемников.
2.1. Ознакомьтесь с файлом openldap-enable-syncrepl-consumer.ldif, устанавливаемым в
составе Alpha.Security:
dn: olcDatabase={1}mdb,cn=config
changetype: modify
#delete: olcSyncrepl
add: olcSyncrepl
olcSyncrepl:
rid=001
provider=ldap://192.168.56.1
binddn="cn=admin,dc=maxcrc,dc=com"
bindmethod=simple
credentials="secret"
searchbase="dc=maxcrc,dc=com"
type=refreshAndPersist
timeout=0
network-timeout=0
retry="60 +"
dn: olcDatabase={1}mdb,cn=config
changetype: modify
#delete: olcUpdateRef
add: olcUpdateRef
olcUpdateRef: ldap://192.168.56.1
Обратите внимание, что отступ в каждой строке внутри конструкции olcSyncRepl обязательно должен
содержать по два пробела.
2.2. Измените следующие строки:
«dn: olcDatabase={1}mdb,cn=config» – замените «{1}mdb» на текущий тип БД, если он
отличается;
«provider=ldap://192.168.56.1» – замените значение по умолчанию «192.168.56.1» на
адрес сервера-поставщика данных;
«credentials="secret"» – если меняли пароль администратора OpenLDAP, замените
«secret» на актуальное значение;
«olcUpdateRef: ldap://192.168.56.1» – замените значение по умолчанию «192.168.56.1»
на адрес сервера-поставщика данных.
2.3. Для применения внесенных изменений выполните команды:
cd /opt/Automiq/Alpha.Security
sudo sh ./openldap-enable-syncrepl-consumer.sh
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
23

=== Page 3 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
2.4. Перезапустите сервис slapd:
sudo systemctl restart slapd
3. Настройте сервер-поставщик:
3.1. Ознакомьтесь с файлом openldap-enable-syncrepl-provider.ldif, устанавливаемым в
составе Alpha.Security:
dn: cn=module{0},cn=config
changetype: modify
add: olcModuleLoad
olcModuleLoad: syncprov.la
dn: olcOverlay=syncprov,olcDatabase={1}mdb,cn=config
changetype: add
objectClass: olcOverlayConfig
objectClass: olcSyncProvConfig
olcOverlay: syncprov
olcSpNoPresent: TRUE
olcSpCheckpoint: 100 10
olcSpSessionlog: 100
dn: olcDatabase={1}mdb,cn=config
changetype: modify
add: olcDbIndex
olcDbIndex: entryCSN eq
-
add: olcDbIndex
olcDbIndex: entryUUID eq
3.2. Замените «{1}mdb» на текущий тип БД, если он отличается, в строках:
«dn: olcOverlay=syncprov,olcDatabase={1}mdb,cn=config»;
«dn: olcDatabase={1}mdb,cn=config»,
3.3. Для применения внесенных изменений выполните команды:
cd /opt/Automiq/Alpha.Security
sudo sh ./openldap-enable-syncrepl-provider.sh
3.4. Перезапустите сервис slapd:
sudo systemctl restart slapd
24
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 4 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
4. Настройте Агент Alpha.Security:
4.1. Перейдите к файлу конфигурации alpha.security.agent.xml, расположенному в
/opt/Automiq/Alpha.Security. Добавьте в секцию элемента <LdapHosts> строки с IP-адресами и
портами всех резервируемых серверов:
<LdapHosts>
<LDAPServer Address="127.0.0.1" Port="389"/>
<LDAPServer Address="172.16.13.167" Port="389"/>
</LdapHosts>
В данном примере:
«127.0.0.1» – адрес локального сервера (поставщика);
«172.16.13.167» – пример адреса сервера-приемника (укажите нужный адрес).
4.2. Перезапустите сервис агента безопасности:
sudo systemctl restart alpha.security.service
3.2.3.2. Разнонаправленное резервирование
Прежде чем перейти к настройкам резервирования:
1. Убедитесь, что типы баз данных всех серверов – «mdb», с помощью команды:
sudo slapcat -n0
Пример искомого значения: «dn: olcDatabase={1}mdb,cn=config». Если тип БД отличается, то во всех
файлах, создаваемых и применяемых в инструкции ниже, следует указывать правильный тип базы.
2. Отключите все возможные репликации баз и серверов. Исключите вероятность подключения
клиентских приложений к агенту безопасности, а агента безопасности – к резервируемым серверам.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
25

=== Page 5 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
3. Убедитесь, что содержимое баз резервируемых серверов идентично. Чтобы синхронизировать
содержимое баз данных, можно БД одного из серверов скопировать на все резервируемые сервера
путем копирования файлов базы.
Обратите внимание, что резервная копия базы, созданная с помощью Alpha.HMI.SecurityConfigurator,
не подходит для синхронизации содержимого баз данных. Выполните действия, описанные ниже.
3.1. Скопируйте базу, расположенную в каталоге /var/lib/ldap на выбранном сервере. Пусть
скопированная база считается эталонной.
3.2. На резервируемом сервере, на котором нужно заменить базу на эталонную:
3.2.1. Проверьте владельца файлов БД с помощью команды: 
ps aux | grep openldap
Нужная строка с владельцем выглядит следующим образом:
/usr/sbin/slapd -h ldap:/// ldaps:/// ldapi:/// -g openldap -u openldap -F
/etc/ldap/slapd.d
Владелец по умолчанию – openldap.
3.2.2. Замените файлы в папке /var/lib/ldap, на эталонные, скопированные ранее.
3.2.3. Переназначьте владельца у скопированных файлов с помощью команды:
chown -R openldap:openldap /var/lib/ldap
3.2.4. Перезапустите сервис slapd.
4. Сделайте бэкап конфигурации с помощью команды:
cd /opt/Automiq/Alpha.Security
sudo sh ./openldap-conf-and-data-backup.sh
Для восстановления конфигурации и БД OpenLDAP в случае ошибок резервирования, выполните
команды:
cd /opt/Automiq/Alpha.Security
sudo sh ./openldap-conf-and-data-restore.sh
5. Остановите все программы, взаимодействующие с серверами OpenLDAP.
6. Убедитесь, что системное время резервируемых серверов одинаковое, иначе синхронизация
изменений будет работать в одну сторону.
7. На время настройки резервирования одного из серверов остановите остальные резервируемые
сервера OpenLDAP.
26
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 6 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
Чтобы настроить разнонаправленное резервирование:
1. На любом из резервируемых серверов создайте файл конфигурации резервирования.
ПРИМЕЧАНИЕ
Можно не создавать и тиражировать файл, а воспользоваться шаблонами файлов для двух
резервируемых серверов, поставляемыми в составе дистрибутива Alpha.Security:
openldap-enable-syncrepl-multiprovider-server-1.ldif;
openldap-enable-syncrepl-multiprovider-server-1.sh;
openldap-enable-syncrepl-multiprovider-server-2.ldif;
openldap-enable-syncrepl-multiprovider-server-2.sh.
Файлы необходимо редактировать так, как описано ниже.
Назовите файл openldap-enable-syncrepl-multiprovider-server.ldif, добавьте в него следующее:
##########################################################
# Check/modify database type (bdb/hdb/mbd/...), server ID (unique number),
# address of provider, binddn, credentials, searchbase.
##########################################################
dn: cn=module,cn=config
objectClass: olcModuleList
cn: module
olcModulePath: /usr/lib/ldap
olcModuleLoad: syncprov.la
##########################################################
dn: olcOverlay=syncprov,olcDatabase={1}mdb,cn=config
objectClass: olcOverlayConfig
objectClass: olcSyncProvConfig
olcOverlay: syncprov
olcSpSessionLog: 100
##########################################################
dn: cn=config
changetype: modify
replace: olcServerID
olcServerID: 1
dn: olcDatabase={1}mdb,cn=config
changetype: modify
add: olcSyncRepl
olcSyncRepl:
rid=001
provider=ldap://192.168.56.102:389
bindmethod=simple
binddn="cn=admin,dc=maxcrc,dc=com"
credentials="secret"
searchbase="dc=maxcrc,dc=com"
scope=sub
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
27

=== Page 7 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
schemachecking=on
type=refreshAndPersist
retry="30 5 300 3"
interval=00:00:05:00
-
add: olcMirrorMode
olcMirrorMode: TRUE
Обратите внимание, что отступ в каждой строке внутри конструкции olcSyncRepl обязательно должен
содержать по два пробела.
28
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 8 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
2. Измените файл конфигурации следующим образом:
2.1. В строке olcServerID: 1 придумайте и укажите идентификатор сервера;
ОБРАТИТЕ ВНИМАНИЕ
olcServerID должен быть уникальным для каждого резервируемого сервера.
2.2. Замените «{1}mdb» на текущий тип БД, если он отличается, в строках:
«dn: olcDatabase={1}mdb,cn=config»;
«dn: olcOverlay=syncprov,olcDatabase={1}mdb,cn=config»
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
29

=== Page 9 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
2.3. Добавьте столько конструкций olcSyncRepl, сколько серверов резервируют текущий сервер.
Каждая конструкция olcSyncRepl описывает один из резервируемых серверов.
ОБРАТИТЕ ВНИМАНИЕ
Внутри одного сервера параметры rid разных конструкций olcSyncRepl должны иметь
уникальные значения.
Например, если текущий сервер резервируют сразу два сервера, конструкций olcSyncRepl в файле
будет две. Пример:
##########################################################
# Check/modify database type (bdb/hdb/mbd/...), server ID (unique number),
# address of provider, binddn, credentials, searchbase.
##########################################################
dn: cn=module,cn=config
objectClass: olcModuleList
cn: module
olcModulePath: /usr/lib/ldap
olcModuleLoad: syncprov.la
##########################################################
dn: olcOverlay=syncprov,olcDatabase={1}mdb,cn=config
objectClass: olcOverlayConfig
objectClass: olcSyncProvConfig
olcOverlay: syncprov
olcSpSessionLog: 100
##########################################################
dn: cn=config
changetype: modify
replace: olcServerID
olcServerID: 1
dn: olcDatabase={1}mdb,cn=config
changetype: modify
add: olcSyncRepl
olcSyncRepl:
rid=001
provider=ldap://192.168.56.102:389
bindmethod=simple
binddn="cn=admin,dc=maxcrc,dc=com"
credentials="secret"
searchbase="dc=maxcrc,dc=com"
scope=sub
schemachecking=on
type=refreshAndPersist
retry="30 5 300 3"
interval=00:00:05:00
olcSyncRepl:
30
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 10 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
rid=002
provider=ldap://192.168.57.102:389
bindmethod=simple
binddn="cn=admin,dc=maxcrc,dc=com"
credentials="secret"
searchbase="dc=maxcrc,dc=com"
scope=sub
schemachecking=on
type=refreshAndPersist
retry="30 5 300 3"
interval=00:00:05:00
-
add: olcMirrorMode
olcMirrorMode: TRUE
2.4. В каждой конструкции olcSyncRepl укажите IP-адрес и порт сервера, который она описывает, в
строке параметра provider.
3. Для применения внесенных изменений выполните команду:
sudo ldapadd -Y EXTERNAL -H ldapi:/// -f openldap-enable-syncrepl-
multiprovider-server.ldif
4. Перезапустите сервис slapd:
sudo systemctl restart slapd
5. Повторите все описанные действия на каждом из резервируемых серверов.
6. Настройте Агент Alpha.Security:
6.1. Перейдите к файлу конфигурации alpha.security.agent.xml, расположенному в
/opt/Automiq/Alpha.Security. Добавьте в секцию элемента <LdapHosts> строки с IP-адресами и
портами всех резервируемых серверов:
<LdapHosts>
<LDAPServer Address="127.0.0.1" Port="389"/>
<LDAPServer Address="172.16.13.167" Port="389"/>
</LdapHosts>
В данном примере:
«127.0.0.1» – адрес локального сервера (поставщика);
«172.16.13.167» – пример адреса сервера-приемника (укажите нужный адрес).
6.2. Перезапустите сервис агента безопасности:
sudo systemctl restart alpha.security.service
После настройки последовательно включите все сервера OpenLDAP. Подключитесь напрямую к каждой базе
и убедитесь, что ошибок не возникло. Для проверки внесите изменения в конфигурацию на одном из
серверов. Убедитесь, что эти изменения появились и на других серверах.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
31

=== Page 11 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
3.3. Для пользователей РЕД ОС
Ниже приведена инструкция по настройке OpenLDAP для РЕД ОС.
Все команды настройки OpenLDAP необходимо выполнять от имени суперпользователя root. Для этого перед
вводом каждой команды введите sudo, либо, прежде чем вводить команды, перейдите в режим
суперпользователя с помощью команды su.
При настройке OpenLDAP понадобится редактировать конфигурационные файлы. Для создания и
редактирования текстовых файлов на ОС Linux предлагается использовать редактор NANO. Команда nano
позволяет открыть существующий или создать новый файл с указанным именем. В результате вызова
команды файл откроется в соответствующем редакторе.
Если используете редактор NANO, то:
чтобы сохранить файл, нажмите сочетание клавиш Ctrl + O;
чтобы выйти из редактора, нажмите сочетание клавиш Ctrl + X;
чтобы вызвать справку, нажмите сочетание клавиш Ctrl + G.
ОБРАТИТЕ ВНИМАНИЕ
Текстовые файлы (файлы-схемы, LDIF-файлы), служащие для настройки OpenLDAP, формируются
с учетом следующих правил:
пробелы и табуляция недопустимы перед ключевыми словами (overlay, index, syncrepl,
updateref, и т.п.);
там, где пробелы используются для отступа в начале строки для улучшения читаемости
текста, следует ставить два пробела подряд.
Будьте внимательны при копировании текстовых блоков из этого раздела (в нем правила
формирования файлов учтены) и при редактировании файлов вручную.
3.3.1. Настройка OpenLDAP
Предварительно:
1. Убедитесь, что установили пакеты, необходимые для доступа и изменения каталогов OpenLDAP, как
описано в разделе 2. Установка и удаление (стр. 7).
2. Проверьте имя и тип базы данных (hdb, mdb, и т.п.) с помощью команды:
sudo slapcat -n0
Пример искомого значения: «dn: olcDatabase={2}mdb,cn=config». Если база имеет тип, отличный от
{2}mdb, во всех файлах, создаваемых и применяемых в инструкции ниже, следует указывать
правильный тип базы.
3. Разрешите доступ через брандмауэр с помощью команды:
sudo firewall-cmd --add-service=ldap
32
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 12 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
4. Сгенерируйте шифрованное значение пароля для учетной записи администратора LDAP с помощью
команды:
slappasswd
Шифрованное значение имеет вид {SSHA}строка_символов. Сохраните полученное значение для
следующих шагов настройки.
Затем последовательно выполните действия, описанные в подразделах ниже.
Применение схем для создания УЗ администратора и политик контроля
доступа
Перейдите к каталогу /opt/Automiq/Alpha.Security. Здесь для настройки OpenLDAP нужно применить LDIF-
файлы, один из которых поставляется в составе дистрибутива, а еще два необходимо создать
самостоятельно.
1. Создайте и примените LDIF-файл config.ldif, который используется для задания пароля учетной
записи администратора LDAP (olcRootPW).
1.1. Создайте файл командой:
sudo nano config.ldif
1.2. Добавьте в файл следующее:
dn: olcDatabase={0}config,cn=config
changetype: modify
add: olcRootPW
olcRootPW: {SSHA}строка_символов
olcDatabase – указывает конкретное имя экземпляра базы данных и обычно находится в
/etc/ldap/slapd.d/cn=config;
cn=config – указывает глобальные параметры конфигурации;
{SSHA}строка_символов – шифрованное значение пароля администратора, полученное ранее.
1.3. Примените файл командой:
sudo ldapadd -Y EXTERNAL -H ldapi:/// -f config.ldif
В случае успешного завершения операции должно появиться следующее сообщение:
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
33

=== Page 13 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
2. Создайте и примените LDIF-файл db.ldif, который используется для добавления учетной записи
администратора LDAP (olcRootDN).
2.1. Создайте файл командой:
sudo nano db.ldif
2.2. Добавьте в файл следующее:
dn: olcDatabase={2}mdb,cn=config
changetype: modify
replace: olcSuffix
olcSuffix: dc=maxcrc,dc=com
dn: olcDatabase={2}mdb,cn=config
changetype: modify
replace: olcRootDN
olcRootDN: cn=admin,dc=maxcrc,dc=com
dn: olcDatabase={2}mdb,cn=config
changetype: modify
add: olcRootPW
olcRootPW: {SSHA}строка_символов
где {SSHA}строка_символов – шифрованное значение пароля администратора, полученное ранее, а
вместо {2}mdb следует указать тип вашей базы.
2.3. Примените созданный файл командой:
sudo ldapadd -Y EXTERNAL -H ldapi:/// -f db.ldif
В случае успешного завершения операции должно появиться следующее сообщение:
34
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 14 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
3. Примените LDIF-файл access.ldif, поставляемый в составе дистрибутива Alpha.Security для
применения политик контроля доступа, командой:
sudo ldapadd -Y EXTERNAL -H ldapi:/// -f access.ldif
ОБРАТИТЕ ВНИМАНИЕ
Проверьте содержимое файла access.ldif. Оно должно выглядеть следующим образом:
dn: olcDatabase={2}mdb,cn=config
changetype: modify
replace: olcAccess
olcAccess: {0}to * by users write by * read
На месте {2}mdb должен быть указан тип вашей базы, как в остальных пунктах инструкции.
В случае успешного завершения операции должно появиться следующее сообщение:
Применение схем OpenLDAP
Теперь необходимо применить файлы-схемы, поставляемые вместе с OpenLDAP.
1. Перейдите к папке, где хранятся файлы.
cd /etc/openldap/schema/
2. Затем примените файлы-схемы в том порядке, в котором они перечислены ниже. Обратите внимание,
что в РЕД ОС версии 8.0 отсутствует файл /etc/openldap/schema/ppolicy.ldif, применять его не
нужно.
sudo ldapadd -Q -Y EXTERNAL -H ldapi:/// -f collective.ldif
sudo ldapadd -Q -Y EXTERNAL -H ldapi:/// -f corba.ldif
sudo ldapadd -Q -Y EXTERNAL -H ldapi:/// -f cosine.ldif
sudo ldapadd -Q -Y EXTERNAL -H ldapi:/// -f duaconf.ldif
sudo ldapadd -Q -Y EXTERNAL -H ldapi:/// -f dyngroup.ldif
sudo ldapadd -Q -Y EXTERNAL -H ldapi:/// -f inetorgperson.ldif
sudo ldapadd -Q -Y EXTERNAL -H ldapi:/// -f java.ldif
sudo ldapadd -Q -Y EXTERNAL -H ldapi:/// -f misc.ldif
sudo ldapadd -Q -Y EXTERNAL -H ldapi:/// -f nis.ldif
sudo ldapadd -Q -Y EXTERNAL -H ldapi:/// -f openldap.ldif
sudo ldapadd -Q -Y EXTERNAL -H ldapi:/// -f pmi.ldif
sudo ldapadd -Q -Y EXTERNAL -H ldapi:/// -f ppolicy.ldif
После выполнения каждой команды должно появляться сообщение об успешном применении схемы:
Применение схемы Alpha.Security
Далее необходимо применить схему, поставляемую вместе с дистрибутивом Alpha.Security.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
35

=== Page 15 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
1. Вернитесь в каталог установки агента безопасности.
cd /opt/Automiq/Alpha.Security
2. Примените здесь файл-схему alpha.security.ldif.
sudo ldapadd -Q -Y EXTERNAL -H ldapi:/// -f alpha.security.ldif
Применение схемы домена
Теперь необходимо создать и применить файл-схему, где будет указан так называемый домен, в котором
функционирует агент безопасности.
1. Перейдите к каталогу на уровень выше.
cd /opt/Automiq
2. Создайте файл-схему empty.ldif.
sudo nano empty.ldif
Добавьте в файл следующее:
dn: dc=maxcrc,dc=com
objectClass: domain
objectClass: top
dc: maxcrc
3. Примените созданный файл командой:
sudo ldapadd -x -D 'cn=admin,dc=maxcrc,dc=com' -w secret -H ldapi:/// -f
empty.ldif
где вместо admin следует указать логин администратора LDAP («admin» – значение по умолчанию), а
вместо secret – пароль администратора LDAP в незашифрованном виде.
Затем запустите сервис alpha.security.useractivity.service, как описано в разделе 5. Запуск сервисов
(для ОС Linux) (стр. 70).
Укажите созданную выше учетную запись администратора LDAP в настройках агента безопасности. Как это
сделать – описано в разделе Агент безопасности и его настройка (стр. 65), подраздел "Указать
администратора LDAP" (стр. 65).
Импорт настроек модуля мониторинга
Далее импортируйте настройки модуля мониторинга для того, чтобы он отслеживал длительность сессий и
блокировок пользователей.
1. Перейдите в папку установки Alpha.Security:
cd /opt/Automiq/Alpha.Security
36
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 16 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
2. Примените настройки модуля с помощью команды:
sudo sh ./redosMonitor.sh
Завершение настроек и создание каталога на LDAP-сервере
По завершении всех описанных выше действий перезапустите сервисы агента безопасности и OpenLDAP для
применения новых настроек.
Теперь сервер OpenLDAP настроен. Чтобы начать создавать учетные записи пользователей, объединять их в
группы и наделять правами, нужно создать каталог на LDAP-сервере, в котором будет храниться
создаваемая конфигурация.
Процесс создания нового каталога на LDAP-сервере и подключения к нему описан в разделе 6.1.
Подключение к LDAP-серверу из SecurityConfigurator (стр. 74). SecurityConfigurator может быть установлен
только на Windows. Обратите внимание, что в таком случае оба компьютера – с Windows и с Linux – должны
быть объединены в сеть Alpha.Net. Подробнее о том, как объединить компьютеры в сеть, можно прочитать в
6.7. Организация кластерного рабочего места (стр. 103), или в документе на Alpha.Domain.
Если возможности использовать SecurityConfigurator на Windows нет, на АРМ с Linux можно установить
Alpha.HMI.SecurityConfigurator. Подробнее о том, как использовать этот конфигуратор и создавать в нем
каталоги, читайте в документации на Alpha.HMI.SecurityConfigurator.
3.3.2. Изменение логина и пароля администратора LDAP-сервера
Если необходимо сменить логин и/или пароль администратора LDAP, выполните следующие шаги.
1. Сгенерируйте шифрованное значение нового пароля для учетной записи администратора LDAP с
помощью команды:
slappasswd
Шифрованное значение имеет вид {SSHA}строка_символов. Сохраните полученное значение для
следующих шагов настройки.
2. Проверьте имя и тип базы данных (hdb, mdb, и т.п.) с помощью команды:
slapcat -n0
Пример искомого значения: «dn: olcDatabase={2}mdb,cn=config».
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
37

=== Page 17 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
3. Создайте файл-схему change-rootdn.ldif. Добавьте в файл текст в зависимости от того, какие
данные нужно изменить:
Если нужно изменить только логин администратора, добавьте в файл следующее:
dn: olcDatabase={2}mdb,cn=config
changetype: modify
replace: olcRootDN
olcRootDN: cn=newadmin,dc=maxcrc,dc=com
где вместо {2}mdb нужно указать тип вашей базы, определенный на шаге 2, а вместо newadmin –
новый логин администратора.
Если нужно изменить только пароль администратора, добавьте в файл следующее:
dn: olcDatabase={2}mdb,cn=config
changetype: modify
replace: olcRootPW
olcRootPW: {SSHA}строка_символов
где вместо {2}mdb нужно указать тип вашей базы, определенный на шаге 2, а вместо {SSHA}строка_
символов – новый логин администратора.
Если нужно изменить и логин, и пароль администратора, добавьте в файл следующее:
dn: olcDatabase={2}mdb,cn=config
changetype: modify
replace: olcRootDN
olcRootDN: cn=newadmin,dc=maxcrc,dc=com
-
replace: olcRootPW
olcRootPW: {SSHA}строка_символов
где вместо {2}mdb нужно указать тип вашей базы, определенный на шаге 2, вместо newadmin – новый
логин администратора, а вместо {SSHA}строка_символов – новый логин администратора.
4. Примените созданный файл-схему и перезапустите сервис slapd (команды должны выполняться без
ошибок):
sudo ldapadd -Y EXTERNAL -H ldapi:/// -f change-rootdn.ldif
sudo systemctl restart slapd
Пароль администратора LDAP будет изменен.
Обратите внимание, что логин и пароль администратора LDAP нужно указывать в конфигурационном файле
агента безопасности, подробнее об этом – в разделе 4. Агент безопасности и его настройка (стр. 64),
подраздел Указать администратора LDAP (стр. 65).
3.3.3. Резервирование LDAP-сервера
Резервирование (репликация) LDAP-сервера позволяет синхронизировать конфигурации двух и более
серверов. Резервирование может быть:
однонаправленным – в этом случае конфигурация одного сервера (поставщика) тиражируется на
другие сервера (приемники);
38
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 18 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
разнонаправленным – в этом случае синхронизируются конфигурации нескольких серверов.
3.3.3.1. Однонаправленное резервирование
Прежде чем перейти к настройкам резервирования:
1. Убедитесь, что типы баз данных всех серверов – «mdb», с помощью команды:
sudo slapcat -n0
Пример искомого значения: «dn: olcDatabase={2}mdb,cn=config». Если база имеет тип, отличный от
«{2}mdb», то во всех файлах, создаваемых и применяемых в инструкции ниже, следует указывать
правильный тип базы.
2. Сделайте бэкап конфигурации и БД сервера-поставщика в текущей папке с помощью команды:
cd /opt/Automiq/Alpha.Security
sudo sh ./openldap-conf-and-data-backup.sh
Для восстановления конфигурации и БД OpenLDAP в случае ошибок резервирования, выполните
команды:
cd /opt/Automiq/Alpha.Security
sudo sh ./openldap-conf-and-data-restore.sh
3. На время настройки резервирования остановите все резервируемые сервера OpenLDAP.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
39

=== Page 19 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
Чтобы настроить однонаправленное резервирование:
1. Определите, какой из LDAP-серверов будет поставщиком, а какие – приемниками.
2. Настройте сервера-приемники:
ОБРАТИТЕ ВНИМАНИЕ
Описанные в пункте действия выполните на каждом из серверов-приемников.
2.1. Ознакомьтесь с файлом openldap-enable-syncrepl-consumer.ldif, устанавливаемым в
составе Alpha.Security:
dn: olcDatabase={2}mdb,cn=config
changetype: modify
#delete: olcSyncrepl
add: olcSyncrepl
olcSyncrepl:
rid=001
provider=ldap://192.168.56.1
binddn="cn=admin,dc=maxcrc,dc=com"
bindmethod=simple
credentials="secret"
searchbase="dc=maxcrc,dc=com"
type=refreshAndPersist
timeout=0
network-timeout=0
retry="60 +"
dn: olcDatabase={2}mdb,cn=config
changetype: modify
#delete: olcUpdateRef
add: olcUpdateRef
olcUpdateRef: ldap://192.168.56.1
Обратите внимание, что отступ в каждой строке внутри конструкции olcSyncRepl обязательно должен
содержать по два пробела.
2.2. Измените следующие строки:
«dn: olcDatabase={2}mdb,cn=config» – замените «{2}mdb» на текущий тип БД, если он
отличается;
«provider=ldap://192.168.56.1» – замените значение по умолчанию «192.168.56.1» на
адрес сервера-поставщика данных;
«credentials="secret"» – если меняли пароль администратора OpenLDAP, замените
«secret» на актуальное значение;
«olcUpdateRef: ldap://192.168.56.1» – замените значение по умолчанию «192.168.56.1»
на адрес сервера-поставщика данных.
ОБРАТИТЕ ВНИМАНИЕ
В файлах .ldif порядок и количество пробелов имеют важное значение.
2.3. Для применения внесенных изменений выполните команды:
cd /opt/Automiq/Alpha.Security
sudo sh ./openldap-enable-syncrepl-consumer.sh
40
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 20 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
2.4. Перезапустите сервис slapd:
sudo systemctl restart slapd
3. Настройте сервер-поставщик:
3.1. Ознакомьтесь с файлом openldap-enable-syncrepl-provider.ldif, устанавливаемым в
составе Alpha.Security:
dn: cn=module{0},cn=config
changetype: modify
add: olcModuleLoad
olcModuleLoad: syncprov.la
dn: olcOverlay=syncprov,olcDatabase={2}mdb,cn=config
changetype: add
objectClass: olcOverlayConfig
objectClass: olcSyncProvConfig
olcOverlay: syncprov
olcSpNoPresent: TRUE
olcSpCheckpoint: 100 10
olcSpSessionlog: 100
dn: olcDatabase={2}mdb,cn=config
changetype: modify
add: olcDbIndex
olcDbIndex: entryCSN eq
-
add: olcDbIndex
olcDbIndex: entryUUID eq
3.2. Замените «{2}mdb» на текущий тип БД, если он отличается, в строках:
«dn: olcOverlay=syncprov,olcDatabase={2}mdb,cn=config»;
«dn: olcDatabase={2}mdb,cn=config»,
3.3. Для применения внесенных изменений выполните команды:
cd /opt/Automiq/Alpha.Security
sudo sh ./openldap-enable-syncrepl-provider.sh
3.4. Перезапустите сервис slapd:
sudo systemctl restart slapd
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
41

=== Page 21 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
4. Настройте Агент Alpha.Security:
4.1. Перейдите к файлу конфигурации alpha.security.agent.xml, расположенному в
/opt/Automiq/Alpha.Security. Добавьте в секцию элемента <LdapHosts> строки с IP-адресами и
портами всех резервируемых серверов:
<LdapHosts>
<LDAPServer Address="127.0.0.1" Port="389"/>
<LDAPServer Address="172.16.13.167" Port="389"/>
</LdapHosts>
В данном примере:
«127.0.0.1» – адрес локального сервера (поставщика);
«172.16.13.167» – пример адреса сервера-приемника (укажите нужный адрес).
4.2. Перезапустите сервис агента безопасности:
sudo systemctl restart alpha.security.service
3.3.3.2. Разнонаправленное резервирование
Прежде чем перейти к настройкам резервирования:
1. Убедитесь, что типы баз данных всех серверов – «mdb», с помощью команды:
sudo slapcat -n0
Пример искомого значения: «dn: olcDatabase={2}mdb,cn=config». Если база имеет тип, отличный от
«{2}mdb», во всех файлах, создаваемых и применяемых в инструкции ниже, следует указывать
правильный тип базы.
2. Отключите все возможные репликации баз и серверов.
3. Убедитесь, что содержимое баз резервируемых серверов идентично.
4. Сделайте бэкап конфигурации с помощью команды:
cd /opt/Automiq/Alpha.Security
sudo sh ./openldap-conf-and-data-backup.sh
Для восстановления конфигурации и БД OpenLDAP в случае ошибок резервирования, выполните
команды:
cd /opt/Automiq/Alpha.Security
sudo sh ./openldap-conf-and-data-restore.sh
5. Остановите все программы, взаимодействующие с серверами OpenLDAP.
6. Убедитесь, что системное время резервируемых серверов одинаковое, иначе синхронизация
изменений будет работать в одну сторону.
7. На время настройки резервирования одного из серверов остановите остальные резервируемые
сервера OpenLDAP.
42
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 22 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
Чтобы настроить разнонаправленное резервирование:
1. На любом из резервируемых серверов создайте файл конфигурации openldap-enable-syncrepl-
multiprovider-server.ldif со следующим содержанием:
##########################################################
# Check/modify database type (bdb/hdb/mbd/...), server ID (unique number),
# address of provider, binddn, credentials, searchbase.
##########################################################
dn: cn=module,cn=config
objectClass: olcModuleList
cn: module
olcModulePath: /usr/lib64/openldap/
olcModuleLoad: syncprov.la
##########################################################
dn: olcOverlay=syncprov,olcDatabase={2}mdb,cn=config
objectClass: olcOverlayConfig
objectClass: olcSyncProvConfig
olcOverlay: syncprov
olcSpSessionLog: 100
##########################################################
dn: cn=config
changetype: modify
replace: olcServerID
olcServerID: 1
dn: olcDatabase={2}mdb,cn=config
changetype: modify
add: olcSyncRepl
olcSyncRepl:
rid=001
provider=ldap://102.108.50.102:389
bindmethod=simple
binddn="cn=admin,dc=maxcrc,dc=com"
credentials="secret"
searchbase="dc=maxcrc,dc=com"
scope=sub
schemachecking=on
type=refreshAndPersist
retry="30 5 300 3"
interval=00:00:05:00
olcSyncRepl:
rid=002
provider=ldap://102.108.50.103:389
bindmethod=simple
binddn="cn=admin,dc=maxcrc,dc=com"
credentials="secret"
searchbase="dc=maxcrc,dc=com"
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
43

=== Page 23 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
scope=sub
schemachecking=on
type=refreshAndPersist
retry="30 5 300 3"
interval=00:00:05:00
-
add: olcMirrorMode
olcMirrorMode: TRUE
dn: olcOverlay=syncprov,olcDatabase={2}mdb,cn=config
changetype: add
objectClass: olcOverlayConfig
objectClass: olcSyncProvConfig
olcOverlay: syncprov
Обратите внимание, что отступ в каждой строке внутри конструкции olcSyncRepl обязательно должен
содержать по два пробела.
2. Измените файл конфигурации следующим образом:
2.1. В строке olcServerID: 1 придумайте и укажите идентификатор сервера;
ОБРАТИТЕ ВНИМАНИЕ
olcServerID должен быть уникальным для каждого резервируемого сервера.
2.2. Замените «{2}mdb» на текущий тип БД, если он отличается, в строках:
«dn: olcDatabase={2}mdb,cn=config»;
«dn: olcOverlay=syncprov,olcDatabase={2}mdb,cn=config»
2.3. Добавьте столько конструкций olcSyncRepl, сколько серверов участвуют в резервировании
помимо текущего. Каждая конструкция olcSyncRepl описывает один из резервируемых серверов.
ОБРАТИТЕ ВНИМАНИЕ
Внутри одного сервера параметры rid разных конструкций olcSyncRepl должны иметь
уникальные значения.
2.4. В каждой конструкции olcSyncRepl укажите IP-адрес и порт сервера, который она описывает, в
строке параметра provider.
3. Для применения внесенных изменений выполните команду:
sudo ldapadd -Y EXTERNAL -H ldapi:/// -f openldap-enable-syncrepl-
multiprovider-server.ldif
4. Перезапустите сервис slapd:
sudo systemctl restart slapd
5. Повторите все описанные действия на каждом из резервируемых серверов.
44
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 24 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
6. Настройте Агент Alpha.Security:
6.1. Перейдите к файлу конфигурации alpha.security.agent.xml, расположенному в
/opt/Automiq/Alpha.Security. Добавьте в секцию элемента <LdapHosts> строки с IP-адресами и
портами всех резервируемых серверов:
<LdapHosts>
<LDAPServer Address="127.0.0.1" Port="389"/>
<LDAPServer Address="172.16.13.167" Port="389"/>
</LdapHosts>
В данном примере:
«127.0.0.1» – адрес локального сервера (поставщика);
«172.16.13.167» – пример адреса сервера-приемника (укажите нужный адрес).
6.2. Перезапустите сервис агента безопасности:
sudo systemctl restart alpha.security.service
После настройки последовательно включите все сервера OpenLDAP. Подключитесь напрямую к каждой базе
и убедитесь, что ошибок не возникло. Для проверки внесите изменения в конфигурацию на одном из
серверов. Убедитесь, что эти изменения появились и на других серверах.
3.4. Для пользователей ОС семейства "Альт"
Ниже приведены инструкции по настройке и резервированию OpenLDAP для ОС семейства "Альт".
Все команды настройки OpenLDAP необходимо выполнять от имени суперпользователя root. Для этого перед
вводом каждой команды введите sudo, либо, прежде чем вводить команды, перейдите в режим
суперпользователя с помощью команды su.
При настройке OpenLDAP понадобится редактировать конфигурационные файлы. Для создания и
редактирования текстовых файлов на ОС Linux предлагается использовать редактор NANO. Команда nano
позволяет открыть существующий или создать новый файл с указанным именем. В результате вызова
команды файл откроется в соответствующем редакторе.
Если используете редактор NANO, то:
чтобы сохранить файл, нажмите сочетание клавиш Ctrl + O;
чтобы выйти из редактора, нажмите сочетание клавиш Ctrl + X;
чтобы вызвать справку, нажмите сочетание клавиш Ctrl + G.
ОБРАТИТЕ ВНИМАНИЕ
Текстовые файлы (файлы-схемы, LDIF-файлы), служащие для настройки OpenLDAP, формируются
с учетом следующих правил:
пробелы и табуляция недопустимы перед ключевыми словами (overlay, index, syncrepl,
updateref, и т.п.);
там, где пробелы используются для отступа в начале строки для улучшения читаемости
текста, следует ставить два пробела подряд.
Будьте внимательны при копировании текстовых блоков из этого раздела (в нем правила
формирования файлов учтены) и при редактировании файлов вручную.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
45

=== Page 25 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
Настройка OpenLDAP
Прежде чем перейти к настройке:
1. Убедитесь, что установили пакеты, необходимые для доступа и изменения каталогов OpenLDAP, как
описано в разделе 2. Установка и удаление (стр. 7).
2. Сгенерируйте шифрованное значение пароля для учетной записи администратора LDAP с помощью
команды:
slappasswd
Шифрованное значение имеет вид {SSHA}строка_символов. Сохраните полученное значение для
следующих шагов настройки.
Настройка сервера FTP (vsftpd)
1. Установите сервер с помощью команды:
sudo apt-get install vsftpd anonftp
2. Перейдите к файлу /etc/xinetd.d/vsftpd. Установите disable = no.
3. Перейдите к файлу /etc/xinetd.conf. Закомментируйте only_from = 127.0.0.1.
4. Перезапустите сервис с помощью команды:
sudo service xinetd restart
либо
sudo systemctl restart xinetd.service
Затем разрешите запуск сервиса вместе с операционной системой с помощью команды:
sudo chkconfig xinetd on
либо
sudo systemctl enable xinetd.service
Настройка и запуск сервиса OpenLDAP
Настройте и запустите OpenLDAP.
1. Перейдите к файлу /etc/openldap/slapd.conf.
1.1. Задайте уровень логирования выше установленного по умолчанию – вместо «0» установите «5»:
loglevel 5.
1.2. Убедитесь, что в файле не закомментирована следующая строка: include /etc/openldap/slapd-mdb-
db01.conf. Она подключает содержимое указанного файла.
2. Создайте директорию для хранения баз данных с помощью команды:
sudo mkdir /var/lib/ldap/bases/maxcrc.com
46
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 26 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
3. Перейдите к файлу /etc/openldap/slapd-mdb-db01.conf. Измените в нём следующие строки:
suffix "dc=example,dc=com" замените на suffix "dc=maxcrc,dc=com";
убедитесь, что rootdn "cn=admin,dc=maxcrc,dc=com";
directory /var/lib/ldap/bases/example.com замените на directory /var/lib/ldap/bases/maxcrc.com;
rootpw secret замените на rootpw {SSHA}строка_символов, где {SSHA}строка_символов –
шифрованное значение пароля администратора, полученное ранее;
конструкцию
access to attrs=userPassword
by self write
by anonymous auth
by * none
замените на
access to *
by anonymous read
by users write
добавьте конструкцию в зависимости от версии операционной системы:
для Alt Linux 10 добавьте конструкцию:
database monitor
access to dn.subtree="cn=Monitor"
by dn.exact="cn=admin,dc=maxcrc,dc=com" write
by users write
by * none
для Alt Linux 11 добавьте конструкцию:
database monitor
access to dn.subtree="cn=Monitor"
by dn.exact="cn=admin,dc=maxcrc,dc=com" write
by dn.regex="^uid=([^,]+),ou=Users,ou=([^,]+)Security,dc=maxcrc,dc=com$" write
by self write
by anonymous none
4. Перейдите к файлу /etc/sysconfig/ldap. Далее порядок действий зависит от версии операционной
системы:
для Alt Linux 10 раскомментируйте в файле строку SLAPDURLLIST="'ldapi:/// ldap:/// ldaps:///'".
для Alt Linux 11 раскомментируйте в файле строку SLAPDURLLIST и удалите из нее двойные
кавычки, получится: SLAPDURLLIST='ldapi:/// ldap:/// ldaps:///'.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
47

=== Page 27 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
5. Примените файл схемы security.schema, поставляемый при установке OpenLDAP на Windows, в
директорию /etc/openldap/schema. В ОС Windows файл можно найти в папке C:\Program
Files\OpenLDAP\schema.
5.1. Предоставьте всем пользователям права на чтение скопированного файла схемы с помощью
команды:
sudo chmod a+r /etc/openldap/schema/security.schema
5.2. Затем перейдите к файлу /etc/openldap/slapd.conf. Откройте его в режиме редактирования. В
конец списка подключаемых схем добавьте строку, подключающую скопированный файл схемы:
include /etc/openldap/schema/security.schema.
6. Запустите сервис slapd и разрешите ему запускаться после перезагрузки операционной системы с
помощью команд:
sudo systemctl start slapd
sudo systemctl enable slapd
Убедиться в том, что сервис запущен, и ему разрешено запускаться после перезагрузки ОС, можно с
помощью команд:
sudo systemctl status slapd
sudo journalctl -xeu slapd
7. Создайте еще один файл схемы entry.ldif. Добавьте в него следующие строки:
dn: dc=maxcrc,dc=com
objectClass: organization
objectClass: dcObject
dc: maxcrc
o: com
Сохраните и закройте файл. Примените созданный файл схемы с помощью команды:
sudo ldapadd -x -f entry.ldif -H ldap:/// -D cn=admin,dc=maxcrc,dc=com -w
secret
где вместо secret следует указать пароль администратора LDAP в незашифрованном виде. В результате
успешного выполнения команды в терминале должна появиться строка:
adding new entry "dc=maxcrc,dc=com".
Завершение настроек и создание каталога на LDAP-сервере
По завершении всех описанных выше действий перезапустите сервисы агента безопасности и OpenLDAP для
применения новых настроек.
Теперь сервер OpenLDAP настроен и запущен. Чтобы начать создавать учетные записи пользователей,
объединять их в группы и наделять правами, нужно создать каталог на LDAP-сервере, в котором будет
храниться создаваемая конфигурация.
Процесс создания нового каталога на LDAP-сервере и подключения к нему описан в разделе 6.1.
Подключение к LDAP-серверу из SecurityConfigurator (стр. 74). SecurityConfigurator может быть установлен
48
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 28 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
только на Windows. Обратите внимание, что в таком случае оба компьютера – с Windows и с Linux – должны
быть объединены в сеть Alpha.Net. Подробнее о том, как объединить компьютеры в сеть, можно прочитать в
6.7. Организация кластерного рабочего места (стр. 103), или в документе на Alpha.Domain.
Если возможности использовать SecurityConfigurator на Windows нет, на АРМ с Linux можно установить
Alpha.HMI.SecurityConfigurator. Подробнее о том, как использовать этот конфигуратор и создавать в нем
каталоги, читайте в документации на Alpha.HMI.SecurityConfigurator.
3.4.1. Резервирование LDAP-сервера
Резервирование LDAP-сервера позволяет синхронизировать конфигурации двух и более серверов. Для ОС
семейства "Альт" пока описана только инструкция по настройке разнонаправленного резервирования, при
котором синхронизируются конфигурации нескольких серверов.
Прежде чем перейти к настройкам резервирования:
1. Остановите сервис slapd на всех серверах, которые будут участвовать в резервировании, с помощью
команды:
sudo systemctl stop slapd
Также следует остановить все остальные службы, взаимодействующие с OpenLDAP.
2. Растиражируйте базу одного из резервируемых серверов на остальные сервера, чтобы содержимое
баз резервируемых серверов было идентично. База сервера представляет собой файл DB_CONFIG,
расположенный в папке /var/lib/ldap/bases/maxcrc.com.
Затем на каждом резервируемом сервере:
1. Перейдите к файлу /etc/openldap/slapd.conf. В разделе ##Overlays добавьте или раскомментируйте
строку moduleload<---->syncprov.la.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
49

=== Page 29 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
2. Перейдите к файлу /etc/openldap/slapd-mdb-db01.conf. Сразу после раздела, описывающего
настройки репликации (раздел начинается строкой # Replication setup for this database, и заканчивается
строкой ## Replication setup - end), редактируйте файл следующим образом:
2.1. Добавьте строку с ID текущего сервера:
serverid 1
ID может быть любым, главное, чтобы в пределах группы резервируемых серверов он был
уникальным (например, если у вас два резервируемых сервера, на одном можно указать serverid 1,
на другом – serverid 2).
50
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 30 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
2.2. Сделайте отступ в одну строку и добавьте приведенную ниже конструкцию syncrepl. Эта
конструкция будет описывать один из серверов, резервирующих текущий сервер. Таких конструкций
нужно добавить столько, сколько серверов резервируют текущий сервер (например, если в группе
всего три сервера, здесь будет две конструкции syncrepl):
serverid 1
syncrepl
rid=001
provider=ldap://102.108.50.102:389
bindmethod=simple
binddn="cn=admin,dc=maxcrc,dc=com"
credentials="secret"
searchbase="dc=maxcrc,dc=com"
scope=sub
schemachecking=on
type=refreshAndPersist
retry="30 5 300 3"
interval=00:00:05:00
syncrepl
rid=002
provider=ldap://102.108.50.103:389
bindmethod=simple
binddn="cn=admin,dc=maxcrc,dc=com"
credentials="secret"
searchbase="dc=maxcrc,dc=com"
scope=sub
schemachecking=on
type=refreshAndPersist
retry="30 5 300 3"
interval=00:00:05:00
Здесь, в рамках каждой конструкции syncrepl, нужно указать:
Уникальный в пределах текущего файла rid для описываемого сервера (в строке rid=001).
IP-адрес описываемого сервера (в строке provider=ldap://102.108.50.102:389).
Логин учетной записи администратора описываемого сервера (в строке
binddn="cn=admin,dc=maxcrc,dc=com" – вместо admin).
Пароль учетной записи администратора описываемого сервера в незашифрованном виде (в
строке credentials="secret").
Если же вам необходимо скрыть пароль администратора, то настройка этого блока будет
отличаться: перейдите к подразделу Настройка резервирования без указания пароля
администратора (стр. 52).
2.3. После того, как с помощью конструкций syncrepl опишете все сервера, резервирующие
текущий сервер, снова сделайте отступ в одну строку и добавьте следующий блок:
mirrormode TRUE
overlay syncprov
syncprov-checkpoint 100 1
syncprov-sessionlog 100
index entryCSN eq
index entryUUID eq
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
51

=== Page 31 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
2.4. Сохраните и закройте файл.
После того, как отредактируете оба файла на всех резервируемых серверах, запустите сервис slapd каждого
из них с помощью команды:
sudo systemctl start slapd
Также следует запустить все остальные службы, взаимодействующие с OpenLDAP. Затем можно
подключиться напрямую к каждой базе, чтобы убедиться, что ошибок не возникло. Для проверки внесите
изменения в конфигурацию на одном из серверов. Убедитесь, что эти изменения появились и на других
серверах.
3.4.2. Настройка резервирования без указания пароля администратора
Для того, чтобы не указывать пароль администратора в файле /etc/openldap/slapd-mdb-db01.conf при
настройке резервирования, используйте решение с использованием сертификатов OpenSSL и защищенного
соединения. Необходимо выполнить следующие шаги по порядку:
1. Включить защищенное соединение.
2. Обновить сертификаты безопасности.
3. Настроить резервирование серверов.
Включить защищенное соединение
Для того, чтобы использовать защищенное соединение при подключении к OpenLDAP, выполните
следующие шаги:
1. В файле /etc/sysconfig/ldap раскомментируйте строку:
SLAPDURLLIST="'ldapi:/// ldap:/// ldaps:///'"
2. В файле /etc/openldap/slapd.conf раскомментируйте следующие строки:
TLSCipherSuite HIGH:MEDIUM:+SSLv2
TLSCACertificateFile /var/lib/ssl/cert.pem
TLSCACertificatePath /var/lib/ssl/certs
TLSCertificateFile /var/lib/ssl/certs/slapd.cert
TLSCertificateKeyFile /var/lib/ssl/private/slapd.key
Строку #TLSVerifyClient never при этом следует оставить закомментированной.
3. Перезапустите сервис slapd:
sudo systemctl restart slapd
Теперь при подключении к OpenLDAP можно использовать защищенное соединение. Если есть возможность,
попробуйте подключиться к LDAP-серверу с помощью SecurityConfigurator, установленном на Windows. В
окне подключения установите галочку напротив выбранного протокола безопасности, а адрес LDAP-сервера
укажите в виде «102.108.50.101:xxx», где вместо «102.108.50.101» следует указать IP-адрес OpenLDAP, а
вместо «xxx» – порт подключения:
«636» – если выбрали протокол SSL;
«389» – если выбрали протокол TLS.
52
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 32 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
Потребуется установить сертификат безопасности. Подробнее об этом – в разделе Подключение к LDAP-
серверу из SecurityConfigurator (стр. 78).
Обновить сертификаты безопасности
Если вам необходимо использовать новые сертификаты вместо тех, что предоставляются сервисом slapd
автоматически, необходимо выполнить следующие действия:
1. Измените хостовые имена компьютеров с резервируемыми LDAP-серверами. Сделать это можно,
отредактировав файл /etc/hostname, или выполнив команду:
sudo hostnamectl set-hostname name
где name – хостовое имя.
Для примера далее будут использованы имена двух резервируемых серверов: host-1 и host-2.
Убедитесь, что компьютеры доступны друг для друга, с помощью команды ping name, без
использования IP-адресов.
2. Перегенерируйте сертификат, автоматически предоставляемый сервисом slapd. Для этого удалите
файлы /var/lib/ssl/certs/slapd.cert, /var/lib/ssl/private/slapd.key и
/var/lib/ssl/certs/slapd.csr, затем перезапустите сервис slapd. Новый сертификат будет
автоматически создан и использован сервисом slapd. Убедитесь, что созданы новые файлы вместо
удаленных.
3. Затем на всех компьютерах скопируйте сгенерированный сертификат (содержимое файла
/var/lib/ssl/certs/slapd.cert) в конец файла /var/lib/ssl/cert.pem. То же самое проделайте с
сертификатами остальных компьютеров домена, если они будут взаимодействовать с использованием
TLS/SSL.
4. Если по какой-то причине необходимо вручную создать собственный сертификат, следует отключить
вызов ExecStartPre=/usr/bin/cert-sh ... в юнит-файле /lib/systemd/system/slapd.service, а затем
выполнить генерацию и подключение сертификата. Здесь эта процедура не описана, т.к. для
резервирования в большинстве случае достаточно сертификатов slapd.
ПРИМЕЧАНИЕ
В ОС семейства "Альт" при запуске сервиса slapd из юнит-файла службы запускается скрипт
/usr/bin/cert-sh, который выполняет другой скрипт – /usr/bin/cert-sh-functions. В нем
выполняется проверка истечения срока действия сгенерированного им же ранее сертификата, и, если
срок истекает или сертификат отсутствует, то скрипт создает новый сертификат для slapd. В файле
/usr/bin/cert-sh-functions есть параметр, задающий срок действия сертификата (в сутках). Этот
срок можно увеличить.
Настроить резервирование серверов
Чтобы настроить резервирование:
1. На каждом сервере измените значение TLSVerifyClient в файлах slapd.conf:
TLSVerifyClient allow
Здесь же задайте уровень loglevel 5 или больше (до 32767), чтобы видеть сообщения о попытках
выполнения резервирования.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
53

=== Page 33 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
2. На каждом сервере добавьте сертификаты всех резервируемых серверов (содержимое файлов
ldapd.cert), в конец файла /var/lib/ssl/cert.pem. Проверьте доступность соседнего сервера для
каждого сервера с помощью команды ldapsearch. Так, например, на сервере host-1 должно
выполниться без ошибок:
sudo ldapsearch -x -H ldap://host-2 -b "dc=maxcrc,dc=com" -ZZ uid=admin
sudo ldapsearch -x -H ldaps://host-2 -b "dc=maxcrc,dc=com" uid=admin
а на сервере host-2 должно выполниться без ошибок:
sudo ldapsearch -x -H ldap://host-1 -b "dc=maxcrc,dc=com" -ZZ uid=admin
sudo ldapsearch -x -H ldaps://host-1 -b "dc=maxcrc,dc=com" uid=admin
54
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 34 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
3. Теперь нужно проверить успешность репликации баз между серверами по протоколу ldap://. Измените
блок настройки резервирования на все резервируемых серверах в файлах /etc/openldap/slapd-mdb-
db01.conf в зависимости от выбранного метода шифрования:
Если используете TLS, для host-1 укажите:
syncrepl
rid=001
provider=ldap://host-1:389
bindmethod=simple
binddn="cn=admin,dc=maxcrc,dc=com"
credentials="secret"
searchbase="dc=maxcrc,dc=com"
scope=sub
schemachecking=on
type=refreshAndPersist
retry="30 5 300 3"
interval=00:00:05:00
starttls=yes
а для host-2 укажите:
syncrepl
rid=001
provider=ldap://host-2:389
bindmethod=simple
binddn="cn=admin,dc=maxcrc,dc=com"
credentials="secret"
searchbase="dc=maxcrc,dc=com"
scope=sub
schemachecking=on
type=refreshAndPersist
retry="30 5 300 3"
interval=00:00:05:00
starttls=yes
Обратите внимание на то, что имена host-1 и host-2 должны точно совпадать с содержащимися в
сгенерированных и подключенных сертификатах. В противном случае в журнале возникнет ошибка
инициализации TLS (-11) при установке соединения, и репликация не будет выполняться.
После изменения этих блоков перезапустите сервис slapd обоих серверов и убедитесь, что
репликация баз успешно выполняется.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
55

=== Page 35 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
Если используете SSL для host-1 укажите:
syncrepl
rid=001
provider=ldaps://host-1:636
bindmethod=simple
binddn="cn=admin,dc=maxcrc,dc=com"
credentials="secret"
searchbase="dc=maxcrc,dc=com"
scope=sub
schemachecking=on
type=refreshAndPersist
retry="30 5 300 3"
interval=00:00:05:00
а для host-2 укажите:
syncrepl
rid=001
provider=ldaps://host-2:636
bindmethod=simple
binddn="cn=admin,dc=maxcrc,dc=com"
credentials="secret"
searchbase="dc=maxcrc,dc=com"
scope=sub
schemachecking=on
type=refreshAndPersist
retry="30 5 300 3"
interval=00:00:05:00
Обратите внимание на то, что имена host-1 и host-2 должны точно совпадать с содержащимися в
сгенерированных и подключенных сертификатах. В противном случае в журнале возникнет ошибка
инициализации TLS/SSL (-11) при установке соединения, и репликация не будет выполняться.
4. После изменения блоков syncrepl, как описано в пункте 3, на каждом сервере перезапустите сервис
slapd и убедитесь, что репликация баз успешно выполняется.
5. Вернитесь к редактированию файлов /etc/openldap/slapd-mdb-db01.conf на всех резервируемых
серверах. В добавленных вами конструкциях syncrepl нужно вместо строк:
bindmethod=simple
credentials=secret
указать:
bindmethod=sasl
saslmech=EXTERNAL
6. Снова перезапустите сервис slapd на каждом сервере и убедитесь, что репликация баз успешно
выполняется.
56
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 36 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
3.5. Настройка SSL / TLS (для ОС Linux)
Если вам необходимо установить безопасное соединение при подключении к LDAP-серверу, установленному
в ОС Linux, предварительно нужно выполнить настройку SSL / TLS для этого сервера – так, как описано в
данном разделе. Подробнее о самом безопасном подключении – в разделе 6.1. Подключение к LDAP-
серверу из SecurityConfigurator (стр. 74).
Инструкция ниже описана для Ubuntu 16.04. Настройка для Astra Linux и РЕД ОС может отличаться.
Инструкция для ОС семейства "Альт" приведена в разделе 3.4. Для пользователей ОС семейства "Альт"
(стр. 45), в подразделе Настройка резервирования без указания пароля администратора (стр. 52) (см. первые
два пункта).
Для начала создайте собственный сертификат CA, сертификат LDAP-сервера и ключ LDAP-сервера. Для
этого выполните следующие действия:
1. Удалите имеющиеся папки с сертификатами с помощью команд:
sudo rm -rf /etc/ssl/ldap
rm -rf ./demoCA
2. Создайте новую папку для хранения сертификатов с помощью команд:
mkdir -p demoCA
mkdir -p demoCA/private
mkdir -p demoCA/certs
mkdir -p demoCA/newcerts
ПРИМЕЧАНИЕ
По умолчанию в /usr/lib/ssl/openssl.cnf есть такое определение:
# [ CA_default ]:
# dir
= ./demoCA
# Where everything is kept
Отсюда и берется название папки demoCA. Его можно изменить здесь, и далее работать со своим
названием папки, везде указывая его вместо demoCA.
3. Выполните команду, которая создаст файл и запишет в него номер создаваемого сертификата CA:
echo "1001" > demoCA/serial
и затем создайте еще один файл с помощью команды:
touch demoCA/index.txt
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
57

=== Page 37 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
4. Создайте ключ-пароль RSA в специальном файле с помощью команды:
/usr/bin/openssl genrsa -aes256 -out demoCA/private/cakey.pem 4096
Будет предложено придумать пароль, введите, например, «admin», затем еще раз «admin».
Теперь удалите парольную фразу из файла с помощью команды:
/usr/bin/openssl rsa -in demoCA/private/cakey.pem -out
demoCA/private/cakey.pem
Будет запрошен пароль, введите значение, заданное выше (например, «admin»).
5. Создайте сертификат CA с помощью указанной ниже команды. Убедитесь, что common совпадает с
FQDN вашего сервера.
/usr/bin/openssl req -new -x509 -days 3650 -key demoCA/private/cakey.pem
-out demoCA/certs/cacert.pem
В команде выше можно использовать значения по умолчанию (например, «3650» – количество дней
действия сертификата), но при запросе FQDN (полное доменное имя) нужно указать ваше значение
вместо значения host-100.local:
Common Name (e.g. server FQDN or YOUR name) []:host-100.local
6. Сгенерируйте ключ LDAP-сервера с помощью команды:
/usr/bin/openssl genrsa -aes256 -out demoCA/private/ldapserver-key.key 4096
Будет предложено придумать пароль, введите, например, «admin», затем еще раз «admin».
Теперь удалите заданную парольную фразу ключа с помощью команды:
/usr/bin/openssl rsa -in demoCA/private/ldapserver-key.key -out
demoCA/private/ldapserver-key.key
Будет запрошен пароль, введите значение, заданное выше (например, «admin»).
7. Сгенерируйте certificate signing request (CSR) с помощью указанной ниже команды. Нужно
использовать те же значения настроек, которые использовали ранее, при создании файла сертификата:
/usr/bin/openssl req -new -key demoCA/private/ldapserver-key.key
-out demoCA/certs/ldapserver-cert.csr
В команде выше можно использовать значения по умолчанию, но при запросе FQDN (полное доменное
имя) нужно указать ваше значение вместо значения host-100.local:
Common Name (e.g. server FQDN or YOUR name) []:host-100.local
58
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 38 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
8. Сгенерируйте сертификат LDAP-сервера и подпишите его ключом и ранее сгенерированным
сертификатом с помощью команды:
/usr/bin/openssl ca -keyfile demoCA/private/cakey.pem -cert
demoCA/certs/cacert.pem
-in demoCA/certs/ldapserver-cert.csr -out demoCA/certs/ldapserver-cert.crt -
days 3649
Обратите внимание, что если файл demoCA/certs/ldapserver-cert.crt пустой – это ошибка. Ожидаемый
вывод команды:
#Using configuration from /usr/lib/ssl/openssl.cnf
#Check that the request matches the signature
#Signature ok
#Certificate Details:
#
Serial Number: 4097 (0x1001)
#
Validity
#
Not Before: Jan 16 19:44:46 2021 GMT
#
Not After : Jan 16 19:44:46 2022 GMT
#
Subject:
#
countryName
= AU
#
stateOrProvinceName
= Some-State
#
organizationName
= Internet Widgits Pty Ltd
#
commonName
= 192.168.56.101
#
X509v3 extensions:
#
X509v3 Basic Constraints:
#
CA:FALSE
#
Netscape Comment:
#
OpenSSL Generated Certificate
#
X509v3 Subject Key Identifier:
#
EE:84:4A:13:61:69:26:8C:89:DE:C6:92:7D:CA:DC:1B:07:DC:95:EF
#
X509v3 Authority Key Identifier:
#
keyid:B5:28:6B:AF:8B:6D:F3:1F:3C:BB:A2:13:11:16:AE:69:72:0B:F3:ED
#
#Certificate is to be certified until Jan 16 19:44:46 2022 GMT (3650 days)
Потребуется подтверждение подписи и сертификации, на этих шагах ответьте «y»:
#Sign the certificate? [y/n]:y
#1 out of 1 certificate requests certified, commit? [y/n]y
Выполнение команды завершится выводом:
#Write out database with 1 new entries
#Data Base Updated
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
59

=== Page 39 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
9. Проверьте наличие у LDAP-сервера сертификата CA с помощью команды:
/usr/bin/openssl verify -CAfile demoCA/certs/cacert.pem
demoCA/certs/ldapserver-cert.crt
Ожидаемый вывод:
#demoCA/certs/ldapserver-cert.crt: OK
10. Переместите папку для хранения сертификатов в папку LDAP-сервера:
sudo mv demoCA /etc/ssl/ldap
Теперь у вас есть файлы собственного сертификата CA, сертификата LDAP-сервера и ключа LDAP-сервера,
расположенные в папках:
/etc/ssl/ldap/certs/cacert.pem
/etc/ssl/ldap/certs/ldapserver-cert.crt
/etc/ssl/ldap/private/ldapserver-key.key
Примените созданный сертификат. Для этого выполните следующее:
1. Укажите в качестве владельца папки с сертификатами OpenLDAP пользователя «openldap»:
sudo chown -R openldap: /etc/ssl/ldap/
Задайте права доступа:
sudo chmod 0400 /etc/ssl/ldap/private/ldapserver-key.key
2. Этот шаг выполняется только для Ubuntu. Если у вас другая ОС, перейдите к шагу 3.
Перейдите к редактированию usr.sbin.slapd командой:
sudo vi /etc/apparmor.d/usr.sbin.slapd
Добавьте в него следующие строки:
/etc/ssl/ldap/ r,
/etc/ssl/ldap/* r,
/etc/ssl/ldap/certs r,
/etc/ssl/ldap/certs/* r,
/etc/ssl/ldap/newcerts r,
/etc/ssl/ldap/newcerts/* r,
/etc/ssl/ldap/private r,
/etc/ssl/ldap/private/* r,
Затем переинициализируйте AppArmor командой:
sudo /etc/init.d/apparmor restart
или перезагрузите систему командой:
sudo reboot
60
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 40 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
3. Обновите сертификаты TLS сервера OpenLDAP.
3.1. Создайте файл-схему для определения атрибутов TLS с помощью команды:
nano openldap-tls.ldif
3.2. Добавьте в файл следующее:
dn: cn=config
changetype: modify
add: olcTLSCACertificateFile
olcTLSCACertificateFile: /etc/ssl/ldap/certs/cacert.pem
-
replace: olcTLSCertificateFile
olcTLSCertificateFile: /etc/ssl/ldap/certs/ldapserver-cert.crt
-
replace: olcTLSCertificateKeyFile
olcTLSCertificateKeyFile: /etc/ssl/ldap/private/ldapserver-key.key
3.3. Примените созданную схему с помощью команды:
sudo ldapmodify -Y EXTERNAL -H ldapi:/// -f openldap-tls.ldif
Ожидаемый вывод:
#SASL/EXTERNAL authentication started
#SASL username: gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth
#SASL SSF: 0
#modifying entry "cn=config"
3.4. Убедиться, что схема применена, можно с помощью команды:
sudo slapcat -b "cn=config" | grep -E "olcTLS"
Ожидаемый вывод:
#olcTLSCACertificateFile: /etc/ssl/ldap/certs/cacert.pem
#olcTLSCertificateFile: /etc/ssl/ldap/certs/ldapserver-cert.crt
#olcTLSCertificateKeyFile: /etc/ssl/ldap/private/ldapserver-key.key
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
61

=== Page 41 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
4. Проверьте что у пользователя «openldap» есть доступ к сертификату CA, сертификату сервера и
ключу сервера. При выполнении команд не должно быть ошибок. Если ошибки возникают, для ОС Astra
Linux можно выполнить действия, указанные ниже в этом же пункте инструкции.
Команда:
sudo -u openldap file /etc/ssl/ldap/certs/cacert.pem
Ожидаемый вывод:
#/etc/ssl/ldap/certs/cacert.pem: PEM certificate
Команда:
sudo -u openldap file /etc/ssl/ldap/certs/ldapserver-cert.crt
Ожидаемый вывод:
#/etc/ssl/ldap/certs/ldapserver-cert.crt: ASCII text
Команда:
sudo -u openldap file /etc/ssl/ldap/private/ldapserver-key.key
Ожидаемый вывод:
#/etc/ssl/ldap/private/ldapserver-key.key: PEM RSA private key
Если при выполнении этих команд возникают ошибки, для ОС Astra Linux можно выполнить следующее:
4.1. Перейдите к параметрам системы в меню Пуск →Параметры →Безопасность →Управление
доступом →Мандатный контроль целостности.
4.2. В нижней части открывшегося окна параметров слева от поля ввода Фильтр переключите режим
отображения списка пользователей – вместо «Обычные» выберите значение «Системные».
4.3. Найдите системного пользователя «openldap» в обновившемся списке пользователей,
выделите его нажатием левой кнопкой мыши. Затем нажмите кнопку, открывающую настройки для
конкретного пользователя, справа от поля ввода Фильтр и выберите Уровень целостности →
Максимальная целостность →«Высокий».
4.4. Нажмите кнопку Применить.
Если не проделать эти шаги, сертификат всё равно будет работать, однако вывод в указанных командах
не будет соответствовать ожидаемому.
5. Для проверки корректности конфигурации LDAP запустите команду:
sudo slaptest -u
Ожидаемый вывод:
#config file testing succeeded
62
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 42 ===
3. LDAP-СЕРВЕР И ЕГО НАСТРОЙКА
6. Все директивы TLS для клиентов должны располагаться в файле ldap.conf. Если не выполнить этого
условия, клиенты (например, конфигуратор или агент безопасности) не смогут устанавливать безопасное
соединение с сервером. Чтобы избежать этого, скопируйте содержимое файла
/etc/ssl/ldap/certs/cacert.pem и вставьте его в конец файла /etc/ssl/certs/ca-certificates.crt, а
затем перезапустите сервер slapd с помощью команды:
sudo systemctl restart slapd
Затем выполните следующую команду (здесь нужно указать ваш FQDN (полное доменное имя) вместо
значения host-100.local):
gnutls-cli --starttls-proto=ldap --print-cert -p 389 host-100.local
Ожидаемый вывод:
#- Status: The certificate is trusted.
#- Description: (TLS1.3-X.509)-(ECDHE-SECP256R1)-(RSA-PSS-RSAE-SHA256)-(AES-
256-GCM)
#- Options:
#- Handshake was completed
Если вы резервируете сервер OpenLDAP, это условие также нужно учесть:
При однонаправленном резервировании на стороне резервирующих серверов должен быть
установлен сертификат резервируемого сервера (так, содержимое файла cacert.pem
резервируемого сервера должно попасть в файлы ca-certificates.crt всех резервирующих
серверов).
При разнонаправленном (зеркальном) резервировании на каждом сервере должны быть
установлены сертификаты всех остальных серверов (так, содержимое файла cacert.pem каждого
резервируемого сервера должно попасть в файлы ca-certificates.crt всех остальных серверов).
7. Необязательный шаг: включите поддержку ldaps:///. Для этого перейдите к редактированию файла
slapd командой:
sudo nano /etc/default/slapd
Измените строку SLAPD_SERVICES так, чтобы получилось следующее:
SLAPD_SERVICES="ldap:/// ldaps:/// ldapi:///"
8. Перезапустите сервис slapd:
sudo systemctl restart slapd
Сертификаты будут применены, и с LDAP-сервером можно будет установить безопасное соединение.
Протокол безопасного соединения выбирается при подключении, подробнее об этом – в разделе 6.1.
Подключение к LDAP-серверу из SecurityConfigurator (стр. 74).
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
63

=== Page 43 ===
4. АГЕНТ БЕЗОПАСНОСТИ И ЕГО НАСТРОЙКА
4. Агент безопасности и его настройка
Агент безопасности представляет собой:
службу Alpha.Security.Agent на ОС Windows;
сервис alpha.security.service на ОС Linux.
Служба (сервис) выполняет следующие функции:
Передает информацию между компонентами Alpha.Security и программами, использующими сервис
безопасности (например Alpha.HMI.Alarms, Alpha.HMI.Trends и пр.)
Транслирует сообщения аудита безопасности в сигналы Alpha.Server (стр. 110).
Выполняет контроль целостности файлов и предоставляет сообщения о результатах с помощью
компонентов Alpha.HMI.Security (стр. 119).
Подключается к внешним источникам учетных данных (например к доменам) для импорта учетных
записей из внешних источников.
Например, при регистрации пользователя в Alpha.HMI.Alarms, введенные данные проверяются на LDAP-
сервере агентом безопасности. Если данные верны, и пользователь имеет доступ к программе, агент
безопасности запоминает пользователя как текущего, и передает сведения о правах пользователя из LDAP-
сервера в Alpha.HMI.Alarms.
После установки может понадобиться настройка агента безопасности. Для настройки Агент Alpha.Security
редактируйте конфигурационный файл alpha.security.agent.xml, расположенный в:
C:\Program Files\Automiq\Alpha.Security – для ОС Windows;
/opt/Automiq/Alpha.Security – для ОС Linux.
После изменения настроек нужно перезапустить службу Alpha.Security.Agent.
Пример настроенного конфигурационного файла находится в Приложение A: Пример конфигурационного
файла Агент Alpha.Security (стр. 131).
Настроить связь с узлами сети Alpha.Net
Эта настройка необходима для установления связи между агентом безопасности и Net-агентом. Как правило
агенты установлены на одном компьютере, и менять указанные здесь значения не требуется.
Чтобы установить связь Alpha.Security с Net-агентом, в конфигурационном файле укажите адрес точки
доступа Alpha.Net.Agent в качестве значений атрибутов элемента <EntryPointNetAgent>:
Address – IP-адрес Net-агента;
Port – порт для подключения.
<EntryPointNetAgent Address="127.0.0.1" Port="1010"/>
Настроить связь с LDAP-сервером
Эта настройка выполняется в случае, если OpenLDAP и агент безопасности установлены на разных
компьютерах.
64
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 44 ===
4. АГЕНТ БЕЗОПАСНОСТИ И ЕГО НАСТРОЙКА
Чтобы установить связь между Агент Alpha.Security и LDAP-сервером, установленным на другом
компьютере, укажите адрес и порт LDAP-сервера в качестве значений атрибутов элемента <LdapHosts>:
<LdapHosts>
<LDAPServer Address="127.0.0.1" Port="389"/>
</LdapHosts>
Указать администратора LDAP
По умолчанию здесь указан логин стандартной учетной записи администратора LDAP.
Для ОС Windows учетная запись создаётся автоматически при установке Alpha.Security. Логин –
«manager», пароль администратора по умолчанию – «secret», либо указанный при установке
Alpha.Security.
Для ОС Linux учетная запись создаётся при установке OpenLDAP. Логин – «admin», пароль
администратора задается при установке.
Если меняли администратора LDAP, укажите его логин в качестве значения атрибута value элемента
<LdapUser> в указанном виде:
<LdapUser value="cn=Manager,dc=maxcrc,dc=com"/>
ОБРАТИТЕ ВНИМАНИЕ
«dc=maxcrc,dc=com» – домен LDAP-сервера, указываемый для связи с Агент Alpha.Security. Это
значение менять нельзя.
«cn="логин-администратора",dc="домен-базы-данных"» – формат указания каталога, принятый для
OpenLDAP.
Здесь же укажите пароль администратора LDAP в зашифрованном виде в качестве значения атрибута value
элемента <LdapPassword>:
<LdapPassword value="VuZyuLC...JFchMHvKXNeztHoFpe24v2Wl9viv"/>
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
65

=== Page 45 ===
4. АГЕНТ БЕЗОПАСНОСТИ И ЕГО НАСТРОЙКА
ПРИМЕЧАНИЕ
Когда необходимо зашифровать пароль, используйте приложение:
alpha.security.crypter.exe, расположенное в C:\Program
Files\Automiq\Alpha.Security\Utils – для ОС Windows;
alpha.security.crypter, расположенное в /opt/Automiq/Alpha.Security/Utils – для ОС
Linux.
Чтобы получить пароль в зашифрованном виде:
1. Запустите приложение через командную строку (терминал) от имени администратора.
2. Введите шифруемый пароль и нажмите Enter.
3. Зашифрованное значение скопируйте и вставьте в качестве значения атрибута value
элемента <LdapPassword> в конфигурационный файл.
Пароли шифруются с использованием алгоритма Salted SHA-1 и хранятся в виде необратимых хэш-
значений.
Указать пользователя по умолчанию
Можно указать пользователя по умолчанию – пользователя, чьи права используются, когда нет активной
пользовательской сессии. Пользователем по умолчанию может быть любой пользователь из созданных при
конфигурировании LDAP-сервера (стр. 89). В целях безопасности не указывайте пользователя, у которого
есть права на редактирование конфигурации подсистемы безопасности.
Задайте имя пользователя в конфигурационном файле в качестве значения атрибута value элемента
<DefaultUser>:
<DefaultUser value="ИМЯПОЛЬЗОВАТЕЛЯ"/>
Здесь же укажите пароль пользователя по умолчанию в зашифрованном виде в качестве значения атрибута
value элемента <DefaultUserPassword>:
<DefaultUserPassword value="VuZyuLC...JFchMHvKXNeztHoFpe24v2Wl9viv"/>
Указать каталог LDAP для подключения
Этот параметр менять не нужно, если на LDAP-сервере всего один каталог, и он создался автоматически при
запуске службы агента безопасности. Подробнее об этом – в разделе 3. LDAP-сервер и его настройка (стр.
11).
66
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 46 ===
4. АГЕНТ БЕЗОПАСНОСТИ И ЕГО НАСТРОЙКА
Если же на LDAP-сервере хранится несколько разных каталогов (корневых папок), то подключаться по
умолчанию агент будет только к одному из них. Укажите название нужного каталога в качестве значения
атрибута value элемента <SecurityDn>:
<SecurityDn value="ou=AlphaSecurity,dc=maxcrc,dc=com"/>
где «AlphaSecurity» – название каталога по умолчанию.
ОБРАТИТЕ ВНИМАНИЕ
«dc=maxcrc,dc=com» – домен LDAP-сервера, указываемый для связи с агентом безопасности. Это
значение менять нельзя.
«ou="имя-каталога",dc="домен-базы-данных"» – формат указания каталога, принятый для
OpenLDAP.
Изменить уровень логирования
Эта настройка реализована одним из атрибутов элемента <Options> в конфигурационном файле.
Чтобы изменить уровень логирования, назначьте атрибуту LoggerLevel значение:
«0» – чтобы выводить в лог минимум информации о работе Alpha.Security;
«2» – чтобы выводить в лог всю необходимую информацию о работе Alpha.Security;
«5» – чтобы выводить в лог дополнительную информацию о работе Alpha.Security.
ОБРАТИТЕ ВНИМАНИЕ
Рекомендуемое значение – «2». Значение «5» следует использовать только при поиске и анализе
ошибок.
Заблокировать использование горячих клавиш (только для ОС Windows)
Эта настройка реализована одним из атрибутов элемента <Options> в конфигурационном файле.
Чтобы запретить использование горячих клавиш, назначьте в качестве значения атрибута kbDriverString
перечень сочетаний SCAN-кодов клавиш. SCAN-коды клавиш разделяются внутри сочетания символом «+»,
а сами сочетания – символом «;». Перечень SCAN-кодов можно посмотреть в Приложение B: SCAN-коды
клавиш (стр. 133).
ПРИМЕР
kbDriverString="0x1D+0x38+0x53;0x1D+0x2A+0x01;"
Такое значение блокирует сочетания «ctrl+alt+del» и «ctrl+shift+esc».
ОБРАТИТЕ ВНИМАНИЕ
Чтобы блокировка использования сочетаний клавиш выполнялась корректно, необходимо
установить драйвер kbDriver, поставляемый вместе с дистрибутивом Alpha.Security. Для этого
перейдите к расположению C:\Program Files\Automiq\Alpha.Security\kbDriver. Инструкция по
установке драйвера описана в расположенном здесь файле readme_kbdriver_install.txt.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
67

=== Page 47 ===
4. АГЕНТ БЕЗОПАСНОСТИ И ЕГО НАСТРОЙКА
Указать необходимость постоянного запроса значений прав с LDAP-сервера
Эта настройка реализована одним из атрибутов элемента <Options> в конфигурационном файле.
Значение атрибута UseRightsCacheStorage используется для выбора источника данных о правах:
«1» – права пользователя не запрашиваются с LDAP-сервера, используются кэшированные значения
прав;
«0» – права пользователя запрашиваются с LDAP-сервера всегда.
Скрыть пользователя из запрашиваемого списка пользователей
Эта настройка реализована одним из атрибутов элемента <Options> в конфигурационном файле.
Значение атрибута ReducedUserList используется для сокращения списка пользователей,
предоставляемого по запросу:
«1» – по запросу предоставляется сокращенный список пользователей;
«0» – по запросу предоставляется полный список пользователей.
Такой список предоставляется, например, в окне входа в конфигураторе. Чтобы исключить пользователя из
полного списка, назначьте ему право InteractiveLogon с запрещающим значением. Подробнее право
описано в Приложение D: Права системного приложения Alpha.Security (стр. 139).
Транслировать сообщения из системного журнала в сообщения аудита
безопасности (для ОС Linux)
Эта настройка реализована одним из атрибутов элемента <Options> в конфигурационном файле.
Значение атрибута FAMode позволяет настроить трансляцию выбранных сообщений из текстовых файлов
(например, из системного журнала) в сигналы сообщений аудита (стр. 110):
«1» – трансляция сообщений включена;
«0» – трансляция сообщений отключена.
Чтобы выбрать сообщения для трансляции:
1. Перейдите к файлу alpha.security.fa.xml, расположенному в /opt/Automiq/Alpha.Security.
2. Ознакомьтесь с содержанием файла. По умолчанию здесь описаны шаблоны сообщений,
транслируемых из системных журналов /var/log/auth.log и /var/log/secure. Для каждого источника
создан элемент <FileRecords> со вложенным элементом <Records>, внутри которого и описаны
шаблоны сообщений – в элементах <Rec>. Назначение атрибутов элемента описано в этом же файле.
Обратите внимание, что значения атрибута EventType соответствует названиям типов сообщений
аудита – «Normal» или «Admin». Эти названия можно менять – подробнее назначение типов описано в
разделе 7. Аудит безопасности (стр. 110). Если типы были переименованы при настройке аудита, здесь
эти значения тоже нужно изменить.
3. Раскомментируйте конструкции <Rec>, если необходимо транслировать описанные сообщения в
аудит. Создайте собственные конструкции по аналогии, если необходимо транслировать сообщения
иного вида.
68
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 48 ===
4. АГЕНТ БЕЗОПАСНОСТИ И ЕГО НАСТРОЙКА
Настроить подключение к внешним источникам учетных данных
Настройка подключения к внешним источникам выполняется для импорта учетных записей из этих
источников. После настройки подключения импорт можно выполнить средствами Alpha.HMI.Security в
собственном проекте Alpha.HMI, либо с помощью Alpha.HMI.SecurityConfigurator 2.5.0 и новее. Подробнее
об этом – в документации на Alpha.HMI.Security и Alpha.HMI.SecurityConfigurator соответственно.
Описание внешних источников выполняется в элементе <ExternalAuthenticationSource>. Каждый
отдельный источник описывается вложенным в <ExternalAuthenticationSource> элементом
<Source>. Для каждого элемента <Source> следует указать значения следующих атрибутов:
SourceID – уникальный идентификатор внешнего источника;
Address – IP-адрес источника;
Port – порт подключения к источнику;
Secure – флаг использования SSL/TLS при подключении:
«true» – использовать TLS;
«false» – использовать SSL.
Также для каждого источника (элемента <Source>) необходимо:
определить соответствие между полями учетных записей OpenLDAP (login, firstname и др.) и внешнего
источника – в качестве значений атрибутов вложенного элемента <MappedAttributes>;
указать шаблон формирования логина для удаленного источника – в виде значения атрибута value
вложенного элемента <LoginTemplate>.
Пример:
<ExternalAuthenticationSource>
<Source SourceID = "Source1" Address="111.111.1.1" Port="389" Secure = "False"
>
<MappedAttributes login = "uid" fistname = "givenName" midname = "initials"
lastname = "sn" description = "company"
displayname = "displayName" email = "mail" position = "title" objectSid =
"ipaNTSecurityIdentifier" objectGUID = "ipaUniqueID"/>
<LoginTemplate value = "uid={login},cn=users,cn=accounts,{domainDN}" />
</Source>
</ExternalAuthenticationSource>
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
69

=== Page 49 ===
5. ЗАПУСК СЕРВИСОВ (ДЛЯ ОС LINUX)
5. Запуск сервисов (для ОС Linux)
Запуск сервиса alpha.security.useractivity.service
Сервис предназначен для обслуживания сессий пользователя. Именно этот сервис позволяет отследить
длительность сессии и время бездействия пользователя. Благодаря ему происходит автоматический выход
пользователя из системы, если длительность сессии или время бездействия достигло установленного
лимита.
По умолчанию сервис запускается автоматически. Чтобы посмотреть список запущенных сервисов,
используйте команду ps aux. Для удобства поиска отфильтруйте результаты с помощью команды grep:
ps aux | grep alpha.security
Если в списке не будет сервиса alpha.security.useractivity.service, необходимо будет запустить его
вручную.
Сервис запускается для каждого пользователя отдельно. Чтобы запустить сервис для конкретного
пользователя, необходимо редактировать файл alpha.security.useractivity.sh, расположенный в
/opt/Automiq/Alpha.Security.
1. Откройте файл в текстовом редакторе, вызвав команду:
sudo nano alpha.security.useractivity.sh
Значения, которые необходимо изменить, выделены цветом.
#!/bin/sh
# Установите правильный адрес дисплея для графического сервера в переменной окружения
DISPLAY.
# Пример: ":0".
export DISPLAY=":0"
# Установите правильный путь к файлу авторизации для графического сервера
# (для того пользователя, от которого выполняется вход в графическую систему).
# Пример: "/home/user1/.Xauthority".
export XAUTHORITY="/home/user1/.Xauthority"
# Укажите имя пользователя для запуска команды от его имени.
sudo -u user1 /opt/Automiq/Alpha.Security/alpha.security.useractivity
2. Здесь:
Укажите значение DISPLAY, зависящее от количества и конфигурации мониторов. Чтобы узнать
значение, вызовите команду:
export |grep DISPLAY
Вместо user1 укажите имя нужного пользователя.
3. Затем нажмите Ctrl + O, чтобы сохранить изменения, и Ctrl + X, чтобы выйти из редактора.
После этого стоит перезапустить систему. Проверьте список запущенных сервисов с помощью команды ps
aux. Сервис alpha.security.useractivity.service будет запущен от имени указанного пользователя.
70
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 50 ===
5. ЗАПУСК СЕРВИСОВ (ДЛЯ ОС LINUX)
Если же необходимо, чтобы сервис следил за сессией еще одного пользователя, необходимо добавить этого
пользователя в конфигурацию сервиса. Для этого перейдите к файлу
alpha.security.useractivity.add.anotheruser.sh, расположенному в /opt/Automiq/Alpha.Security, и
следуйте инструкции, описанной в нем.
Запуск сервисов агента безопасности от имени непривилегированного
пользователя
Сервисы alpha.security.service и alpha.security.useractivity.service, как правило, запущены от
имени суперпользователя root. Чтобы посмотреть, от чьего имени запущен сервис, используйте команду ps
aux. Для удобства поиска отфильтруйте результаты с помощью команды grep:
ps aux | grep alpha.security
Однако в некоторых случаях бывает необходимо разрешить запуск сервиса от имени непривилегированного
пользователя. Для этого выполните следующие шаги:
1. Измените номер порта Net-агента на значение выше «10000» (например, «11010»). Это необходимо,
потому что непривилегированным пользователям нельзя "прослушивать" порты с малыми номерами.
Для этого:
1.1. Перейдите к папке, где хранятся конфигурационные файлы агента безопасности –
/opt/Automiq/Alpha.Security. Замените в конфигурационном файле alpha.security.agent.xml
номер порта Net-агента на новое значение.
1.2. Затем перейдите к папке, где хранятся конфигурационные файлы Alpha.Domain –
/opt/Automiq/Alpha.Domain. Укажите новое значение порта в конфигурационных
файлах alpha.net.agent.xml и alpha.domain.agent.xml.
2. Укажите имя непривилегированного пользователя в юнит-файлах:
2.1. Перейдите к папке, содержащей юнит-файлы: /lib/systemd/system/.
2.2. В файлах alpha.security.service, alpha.security.useractivity.service,
alpha.security.service.backup и alpha.security.useractivity.service.backup замените
значение root в строчках User=root и Group=root на имя непривилегированного пользователя, например
User=test и Group=test.
3. Убедитесь в том, что непривилегированный пользователь имеет права на чтение и запись:
папки установки Alpha.Security;
папок и файлов, для которых выполняется контроль целостности;
кэша конфигурации Alpha.Domain.
После этого следует перезапустить систему. Проверьте список запущенных сервисов с помощью команды
ps aux. Сервисы alpha.security.service и alpha.security.useractivity.service будут запущены от
имени указанного пользователя.
Если сервис alpha.security.useractivity.service по-прежнему не запускается от имени указанного
пользователя, перейдите к редактированию файла
/opt/Automiq/Alpha.Security/alpha.security.useractivity.sh. Удалите из строки:
sudo -u usertest /opt/Automiq/Alpha.Security/alpha.security.useractivity 2>/dev/null
часть "sudo -u usertest", останется строка вида:
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
71

=== Page 51 ===
5. ЗАПУСК СЕРВИСОВ (ДЛЯ ОС LINUX)
/opt/Automiq/Alpha.Security/alpha.security.useractivity 2>/dev/null
Сохраните изменения. После этого перезапустите сервис alpha.security.useractivity.service. Теперь он
должен быть запущен от имени указанного в юнит-файлах пользователя.
72
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 52 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
6. Редактирование конфигурации на LDAP-сервере с
помощью SecurityConfigurator
SecurityConfigurator – это программа для управления содержимым (конфигурирования) каталогов на LDAP-
сервере. SecurityConfigurator позволяет:
создавать учетные записи пользователей;
объединять пользователей в группы для предоставления им одинаковых возможностей;
создавать права доступа к приложениям и группировать права в приложения;
создавать роли в приложениях и назначать их пользователям или группам;
назначать права пользователям или группам;
объединять АРМы, включенные в сеть Alpha.Net, в кластерные рабочие места.
ОБРАТИТЕ ВНИМАНИЕ
SecurityConfigurator разработан только для ОС Windows. Если вы работаете на ОС Linux, можете
использовать кроссплатформенный конфигуратор – Alpha.HMI.SecurityConfigurator.
Однако принцип конфигурирования подсистемы Alpha.Security отличается в зависимости от
используемого конфигуратора.
SecurityConfigurator считается устаревшим. Его можно использовать, однако мы рекомендуем
пользоваться приложением Alpha.HMI.SecurityConfigurator.
Просматривать и редактировать конфигурацию могут только администраторы – пользователи, которым
назначены разрешающие значения прав на просмотр и на редактирование конфигурации (стр. 99).
Чтобы запустить SecurityConfigurator, воспользуйтесь командой Пуск →Automiq →SecurityConfigurator.
ПРИМЕЧАНИЕ
Можно запустить SecurityConfigurator с параметрами. Использование параметров при запуске
позволяет управлять положением и внешним видом окна конфигуратора. Для запуска с параметрами
используйте командную строку.
Возможные параметры запуска конфигуратора описаны в Приложение C: Параметры запуска
SecurityConfigurator (стр. 137).
Раздел описывает создание и редактирование конфигурации на примере пробной конфигурации.
Предположим, все пользователи АРМ на предприятии делятся на две группы: диспетчеры и операторы.
Диспетчеры могут управлять технологическим процессом, а операторы – наблюдать за технологическим
процессом и передавать данные диспетчерам. Все они работают на одном участке. Кроме диспетчеров и
операторов на участке работает начальник участка. Он может и наблюдать за технологическим процессом, и
управлять им. Всем пользователям необходимо иметь возможность воспользоваться любым АРМ на
предприятии.
Тогда, чтобы создать пробную конфигурацию, с помощью конфигуратора необходимо:
1. Создать три группы пользователей – «Диспетчеры»,«Операторы», «Начальники участков».
2. Создать приложение с правами на наблюдение и управление технологическим процессом и назначить
их соответствующим группам пользователей.
3. Создать роль начальника участка в приложении.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
73

=== Page 53 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
4. Создать учетные записи пользователей и поместить их в группы, а также назначить роль начальнику.
5. Объединить в кластерное рабочее место все АРМ предприятия.
Чтобы приступить к созданию такой конфигурации, следует подключиться к LDAP-серверу и создать
каталог.
6.1. Подключение к LDAP-серверу из SecurityConfigurator
SecurityConfigurator может подключаться к LDAP-серверу напрямую, либо с использованием Агент
Alpha.Security. При первом запуске SecurityConfigurator предложит подключиться напрямую к LDAP-
серверу и каталогу, указанным в настройках агента безопасности.
ОБРАТИТЕ ВНИМАНИЕ
После первого подключения напрямую следует настроить подключение с помощью агента
безопасности. Подключение напрямую к LDAP-серверу не позволяет пользоваться всеми
возможностями Alpha.Security. Только при подключении с помощью агента безопасности можно:
пользоваться функцией аудита безопасности (стр. 110);
использовать текущую пользовательскую сессию на разных АРМ, объединенных в
кластерное рабочее место (стр. 103).
Подключение к LDAP-серверу напрямую
При подключении к LDAP-серверу напрямую:
1. В верхнем меню выберите Подключиться....
74
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 54 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
2. В открывшемся окне Подключение к серверу укажите:
адрес LDAP-сервера;
протокол безопасности (снимите галочки, если не собираетесь использовать протокол
безопасности SSL или TLS при подключении. Подробнее об использовании протоколов безопасности
– в Установка безопасного соединения с LDAP-сервером (стр. 78));
корневую папку:
если хотите подключиться к каталогу, созданному автоматически при запуске агента
безопасности, оставьте стандартное название AlphaSecurity;
если хотите создать новый каталог, укажите его название;
если подключаетесь к существующему каталогу, укажите его название.
логин администратора безопасности:
если подключаетесь к каталогу, созданному автоматически при запуске агента
безопасности, укажите «administrator»; 
если создаете собственный каталог, можете указать любой логин – учетная запись
администратора каталога с таким логином будет создана автоматически;
если подключаетесь к существующему каталогу, укажите логин его администратора.
пароль администратора безопасности:
если подключаетесь к каталогу, созданному автоматически при запуске агента
безопасности, укажите «secret»; 
если создаете собственный каталог, можете указать любой пароль для создаваемой
учетной записи администратора каталога;
если подключаетесь к существующему каталогу, укажите пароль его администратора.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
75

=== Page 55 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
3. Нажмите кнопку Проверить или Подключиться. SecurityConfigurator проверит, существует ли каталог
(корневая папка) с указанным именем на LDAP-сервере. Если каталог существует, подключение будет
выполнено успешно.
Если каталог не существует, запустится Мастер создания новой конфигурации, который предложит
создать каталог с указанным именем. В окне мастера:
На вкладке LDAP заполните поля:
Администратор LDAP в формате cn=ИМЯ-АДМИНИСТРАТОРА,dc=ДОМЕН-БАЗЫ-ДАННЫХ
(«manager» – если OpenLDAP установлен на Windows, «admin» – если на Linux);
Пароль администратора LDAP («secret» по умолчанию).
На вкладке Администратор заполните поля:
Администратор безопасности (логин администратора каталога);
Пароль администратора (пароль администратора каталога).
В результате будут созданы:
каталог на LDAP-сервере;
учетная запись администратора Alpha.Security с правами на просмотр и редактирование
созданного каталога.
ПРИМЕЧАНИЕ
В дальнейшем новые каталоги создаются так же: при подключении к LDAP-серверу из
SecurityConfigurator введите нужное имя нового каталога в поле Корневая папка и нажмите
Проверить или Подключиться.
4. После подключения к каталогу станет доступно редактирование его конфигурации от имени
администратора.
76
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 56 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
Подключение к LDAP-серверу с помощью агента безопасности
Чтобы настроить подключение к LDAP-серверу с помощью агента безопасности:
1. В верхнем меню выберите Параметры.
2. В открывшемся окне на вкладке Подключение установите галочку в пункте Подключаться к агенту
системы безопасности.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
77

=== Page 57 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
Теперь при подключении к текущему каталогу достаточно будет вводить только логин администратора и
пароль.
В таком случае при наличии активной пользовательской сессии ввод пароля при запуске конфигуратора
можно сделать необязательным. Для этого необходимо изменить конфигурационный файл
defaultPassReq.xml, расположенный в C:\ProgramData\Automiq\Alpha.SecurityConfigurator.
Ознакомьтесь с этим файлом:
<?xml version="1.0" encoding="utf-8"?>
<Configuration ProductName="Alpha.SecurityConfigurator" ProductVersion="">
<Configurable Id="defaultPassReq">
<DefaultPasswordRequirementsSettings>
<DigitsRequired>true</DigitsRequired>
<UpperRequired>false</UpperRequired>
<LowerRequired>false</LowerRequired>
<SpecialRequired>false</SpecialRequired>
<MinimalPasswordLength>7</MinimalPasswordLength>
<MinimalPasswordHistoryLength>4</MinimalPasswordHistoryLength>
<IdentityConfirmation>true</IdentityConfirmation>
</DefaultPasswordRequirementsSettings>
</Configurable>
</Configuration>
Параметр, регулирующий необходимость подтверждения личности – элемент <IdentityConfirmation>.
Измените значение по умолчанию «true» на «false», чтобы при наличии активной пользовательской сессии
при запуске конфигуратора не требовалось вводить пароль для подтверждения личности.
Подробнее назначение файла и остальных элементов описано в подразделе Изменить начальные значения
прав на уровне приложения (стр. 94).
Установка безопасного соединения с LDAP-сервером
Для защиты соединения при подключении к LDAP-серверу можно выбрать один из протоколов
безопасности: SSL или TLS1. Для использования протокола необходимо установить сертификат.
1SSL и TLS – криптографические протоколы, шифрующие передаваемые данные. После того, как протокол
SSL был стандартизирован IETF (Internet Engineering Task Force), он был переименован в TLS. Поэтому SSL и
TLS отличаются только номером описываемой версии одного и того же протокола.
78
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 58 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
Сертификаты протоколов поставляются вместе с дистрибутивом Alpha.Security. Сертификат достаточно
установить один раз.
При подключении к LDAP-серверу, установленному в ОС Linux, сначала нужно выполнить настройку SSL /
TLS, как описано в разделе 3.5. Настройка SSL / TLS (для ОС Linux) (стр. 57).
В ОС Windows сертификат устанавливается следующим образом:
1. При подключении к LDAP-серверу напрямую из SecurityConfigurator в окне Подключение к серверу
галочкой отметьте название протокола, который хотите использовать. Нажмите Подключиться.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
79

=== Page 59 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
2. Операционная система предложит установить сертификат. Нажмите Установить сертификат....
80
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 60 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
3. В открывшемся окне Мастер импорта сертификатов в области Расположение сертификата выберите
Текущий пользователь и нажмите кнопку Далее.
4. На следующем шаге выберите Поместить все сертификаты в следующее хранилище и нажмите кнопку
Обзор.... В открывшемся окне Выбор хранилища сертификата выберите папку Доверенные корневые
центры сертификации и нажмите ОК. Диалоговое окно закроется.
5. В окне мастера нажмите Далее, а затем – Готово. Подтвердите импорт сертификата в открывшемся
диалоговом окне. В конце концов, в окне мастера появится сообщение Импорт успешно выполнен.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
81

=== Page 61 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
6.2. Создание и редактирование групп пользователей
Чтобы приступить к работе с группами пользователей, перейдите в раздел Группы.
В разделе Группы можно:
создавать и удалять группы;
блокировать и разблокировать группы;
добавлять пользователей в группы;
переходить к редактированию групп.
ПРИМЕР
Для пробной конфигурации создайте группы «Диспетчеры», «Операторы» и «Начальники участка».
Создать группу
В разделе Группы нажмите Добавить на панели инструментов. В создавшемся поле введите название группы.
82
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 62 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
Если в списке уже есть хотя бы одна группа, новую группу можно создать, нажав ПКМ в списке групп и
выбрав Добавить группу из контекстного меню.
Создать дочернюю группу
В группы можно добавлять дочерние группы. Дочерние группы можно использовать, например, когда
необходимо наследовать права родительской группы.
Выберите в списке группу, в которую нужно добавить дочернюю группу, и выберите соответствующий пункт в
контекстном меню по щелчку ПКМ.
Редактировать группу
В разделе Группы выберите группу в списке и нажмите Править на панели инструментов, либо Редактировать
группу в контекстном меню по щелчку ПКМ.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
83

=== Page 63 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
Откроется окно редактирования группы.
В окне редактирования группы можно:
изменить идентификатор группы на LDAP-сервере, изменив значение поля Идентификатор;
изменить отображаемое название группы, изменив значение поля Отображаемое имя;
добавить в группу пользователей и удалить пользователей из группы;
назначить группе роль и лишить роли;
назначить группе права и лишить прав;
удалить группу.
ПРИМЕЧАНИЕ
Чтобы выбрать несколько пользователей при добавлении в группу, используйте комбинацию клавиш
«Ctrl» + «Shift».
Заблокировать группу
Группы можно блокировать. Блокируйте группы, когда необходимо ограничить доступ участников к АРМ.
Пока участник группы заблокирован, его попытки входа отклоняются подсистемой безопасности.
Чтобы заблокировать группу, выберите группу в списке и нажмите Заблокировать группу, либо
Заблокировать группу в контекстном меню по щелчку ПКМ. Заблокированные группы выделяются в списке
серым цветом и курсивом.
Учетные записи пользователей, состоящих в заблокированной группе, в списке пользователей выделяются
серым цветом и жирным шрифтом.
84
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 64 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
6.3. Создание и редактирование прав и приложений
Возможности пользователей в проекте определяются наличием у них разрешений и запретов на
определенные действия. Информация о том, разрешено или запрещено пользователю какое-либо действие,
хранится виде значения права. Права следует создавать внутри приложений. Приложения позволяют
группировать права по какому-либо признаку и создавать роли (стр. 88), которые впоследствии можно
назначать пользователям и группам.
При создании права нужно определить его тип.
Логическое право может иметь одно из двух значений: «разрешено» или «запрещено».
Применяется, когда необходимо разрешать или запрещать какие-либо действия пользователей в
проекте. Например, одному пользователю разрешено печать отчеты (значение права – «true»), а другому
– запрещено (значение права – «false»).
Строковое право в качестве значений предоставляет строки. Одна строка – разрешенное
значение, вторая – запрещенное значение.
Применяется, когда необходимо получить список возможностей пользователя в текстовом виде.
Например, списки отчетов, которые пользователь может и не может печатать.
Чтобы приступить к работе с правами и приложениями, перейдите в раздел Приложения.
В разделе приложений можно:
создавать и удалять приложения;
импортировать приложения из файла и экспортировать в файл;
добавлять в приложения права и удалять права из приложений;
редактировать права;
создавать и удалять роли в приложениях.
ПРИМЕР
Для пробной конфигурации создайте приложение «Участок 1», содержащее права пользователей,
работающих на одном участке:
одно логическое право для доступа к просмотру состояния технологического процесса;
одно логическое право для доступа к управлению технологическим процессом.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
85

=== Page 65 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
Создать приложение
В разделе приложений нажмите Добавить на панели инструментов. В создавшемся поле введите название
приложения.
Если в списке уже есть хотя бы одно приложение, новое приложение можно создать, нажав ПКМ в списке
приложений и выбрав Добавить приложение из контекстного меню.
Добавить право в приложение
Чтобы добавить в приложение право, нажмите Логическое право или Строковое право на панели
инструментов в зависимости от того, право какого типа нужно создать. В создавшемся поле введите
название права.
86
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 66 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
ПРИМЕР
Добавьте в приложение «Участок 1» два логических права:
«Просмотр технологического процесса» – разрешает или запрещает просмотр состояния
технологического процесса;
«Управление технологическим процессом» – разрешает или запрещает управление
технологическим процессом.
Редактировать право
Щелкните на название права в списке.
Откроется окно редактирования права.
В окне редактирования права можно:
редактировать описание права, изменив значение поля Описание;
добавлять и удалять значения права;
назначать значения прав группам и пользователям.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
87

=== Page 67 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
6.4. Создание ролей
Внутри приложения можно создать роль. Роль – это совокупность значений каждого права приложения. Роль
может быть назначена как пользователю, так и группе.
Создание и редактирование ролей ведется в разделе приложений. Чтобы создать роль, выберите
приложение из списка и нажмите Добавить роль. В создавшемся поле введите название роли.
Укажите значения прав для созданной роли:

– разрешающее значение логического права;

– запрещающее значение логического права;

– разрешающее значение строкового права;

– запрещающее значение строкового права;
либо оставьте значение неопределенным:

– для логического права;

– для строкового права.
ПРИМЕР
Создайте роль начальника участка, имеющего разрешения на просмотр и управление
технологическим процессом.
88
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 68 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
6.5. Создание и редактирование учетных записей
Чтобы приступить к работе с учетными записями пользователей, перейдите в раздел Пользователи.
В разделе Пользователи можно:
создавать и удалять учетные записи пользователей;
блокировать и разблокировать пользователей;
принудительно менять пароли учетных записей;
экспортировать список учетных записей в файл.
ПРИМЕР
Для пробной конфигурации создайте трех пользователей – диспетчера, оператора и начальника
участка. При создании поместите пользователей в соответствующие группы. Начальнику участка,
помимо группы, назначьте роль «Начальник участка».
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
89

=== Page 69 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
Создать учетную запись
В разделе Пользователи нажмите Добавить на панели инструментов. Откроется окно создания и
редактирования учетной записи.
Новая учетная запись может быть одного из трех типов:
учетная запись из Active Directory или ОС Windows
;
локальная учетная запись Alpha.Security
;
учетная запись сервера безопасности Iconics
.
Выберите нужный тип учетной записи, переключая иконки.
ПРИМЕЧАНИЕ
Для пробной конфигурации создавайте локальные записи Alpha.Security.
Создать локальную учетную запись Alpha.Security
Заполните обязательные поля:
логин;
пароль;
фамилия;
отображаемое имя (заполняется автоматически и состоит из фамилии, имени и отчества; полученное
90
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 70 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
значение можно менять);
группа.
ПРИМЕЧАНИЕ
Для защиты паролей создаваемых учетных записей используется алгоритм криптографического
хеширования. Полученное хеш-значение является необратимым. Для повышения криптографической
стойкости используется "присаливание" – добавление к паролю неизвестной последовательности
данных перед шифрованием. Это делается для предотвращения декодирования полученного хеш-
значения.
ПРИМЕР
Для пробной конфигурации создайте трех пользователей и добавьте в группы, например:
«Иванов Иван» – в группу «Диспетчеры»;
«Петров Петр» – в группу «Операторы»;
«Семенов Семен» – в группу «Начальники участка», а также назначьте роль «Начальник
участка».
ОБРАТИТЕ ВНИМАНИЕ
Пользователя обязательно добавлять в группу. При этом пользователь может состоять только в
одной группе.
Создать учетную запись из ОС или Iconics
Если выбрать учетную запись из ОС Windows или Iconics, все нужные данные пользователя, кроме группы,
будут подставлены в поля автоматически.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
91

=== Page 71 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
ПРИМЕЧАНИЕ
Прежде чем сохранить учетную запись, добавьте пользователя в группу.
Например, в результате нажатия
откроется окно выбора пользователя из числа пользователей ОС.
Редактировать учетную запись
В разделе Пользователи выберите пользователя в списке и нажмите Просмотр на панели инструментов, либо
Открыть учетную запись пользователя в контекстном меню по щелчку ПКМ.
Откроется окно редактирования учетной записи пользователя. В окне редактирования учетной записи можно:
менять сведения о пользователе (логин, фамилия, имя, телефон и пр.), изменяя значения
соответствующих полей;
изменить пароль пользователя, используя кнопку Задать пароль на панели инструментов;
добавить пользователя в группу и удалить пользователя из группы;
назначить пользователю роль и лишить роли;
назначить пользователю права и лишить прав;
удалить учетную запись пользователя.
92
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 72 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
Заблокировать пользователя
Пользователей можно заблокировать. Блокируйте пользователей, когда необходимо ограничить их доступ к
АРМ. Пока пользователь заблокирован, его попытки входа отклоняются подсистемой безопасности.
Чтобы заблокировать пользователя, выберите пользователя в списке и нажмите Заблокировать
пользователя, либо Заблокировать учетную запись пользователя в контекстном меню по щелчку ПКМ.
Учетные записи заблокированных пользователей выделяются в списке серым цветом.
Фильтровать список пользователей
Фильтрация списка пользователей облегчает поиск пользователей в списке. Фильтровать список можно в
разделе Пользователи, а также при добавлении пользователей в группы. Отображение нужных столбцов
настраивается в контекстном меню.
Чтобы отфильтровать пользователей в разделе Пользователи, нажмите Фильтр на панели
инструментов. Появится строка для ввода названия искомого элемента.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
93

=== Page 73 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
Чтобы фильтровать пользователей при добавлении их в группу или назначая право, в окне Выбор
пользователей нажмите иконку Фильтр. Появится строка для ввода названия искомого элемента.
Изменить начальные значения прав на уровне приложения
При создании новой учетной записи пользователя некоторые права добавляются автоматически. Это права,
управляющие сложностью пароля, его длиной и количеством паролей, хранимых в истории учетной записи.
Настройка начальных значений этих прав возможна в конфигурационном файле defaultPassReq.xml,
расположенном в C:\ProgramData\Automiq\Alpha.SecurityConfigurator. Меняя содержание файла, можно
самостоятельно решать, будут ли добавляться эти права автоматически, и с какими начальными
значениями.
94
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 74 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
ОБРАТИТЕ ВНИМАНИЕ
Перед редактированием конфигурационного файла нужно закрыть SecurityConfigurator.
После редактирования файла:
при создании новых пользователей для автоматически назначенных прав будут установлены
новые значения;
у существующих пользователей значения останутся прежними, пока изменения не будут
сохранены в окне редактирования пользователя.
Ознакомьтесь с содержанием файла:
<?xml version="1.0" encoding="utf-8"?>
<Configuration ProductName="Alpha.SecurityConfigurator" ProductVersion="">
<Configurable Id="defaultPassReq">
<DefaultPasswordRequirementsSettings>
<DigitsRequired>true</DigitsRequired>
<UpperRequired>false</UpperRequired>
<LowerRequired>false</LowerRequired>
<SpecialRequired>false</SpecialRequired>
<MinimalPasswordLength>7</MinimalPasswordLength>
<MinimalPasswordHistoryLength>4</MinimalPasswordHistoryLength>
<IdentityConfirmation>true</IdentityConfirmation>
</DefaultPasswordRequirementsSettings>
</Configurable>
</Configuration>
Внутри элемента <DefaultPasswordRequirementsSettings> во вложенных элементах хранятся
начальные значения прав, автоматически добавляемых новому пользователю при создании новой учетной
записи. В таблице ниже описаны эти элементы и то, как они управляют соответствующими правами.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
95

=== Page 75 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
Элемент
На что влияет
Возможные
значения
Примечание
<DigitsRequired>
соответствует части права Сложность
пароля
Требование к
наличию цифр в
пароле
«true» – в
пароле
должна
содержаться
хотя бы одна
цифра;
«false» –
в пароле не
обязательно
использовать
цифры.
Если «false» установить
для всех элементов,
составляющих право
Сложность пароля, то это
право не будет
автоматически
добавляться пользователю
при создании учетной
записи. Если «true»
установлено хотя бы для
одного элемента, всё право
автоматически
добавляется пользователю
целиком.
<UpperRequired>
соответствует части права Сложность
пароля
Требование к
наличию букв в
верхнем
регистре в
пароле
«true» – в
пароле
должна
содержаться
хотя бы одна
буква в
верхнем
регистре;
«false» –
в пароле не
обязательно
использовать
буквы в
верхнем
регистре.
<LowerRequired>
соответствует части права Сложность
пароля
Требование к
наличию букв в
нижнем
регистре в
пароле
«true» – в
пароле
должна
содержаться
хотя бы одна
буква в
нижнем
регистре;
«false» –
в пароле не
обязательно
использовать
буквы в
нижнем
регистре.
96
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 76 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
Элемент
На что влияет
Возможные
значения
Примечание
<SpecialRequired>
соответствует части права Сложность
пароля
Требование к
наличию
специальных
символов в
пароле
Перечень
специальных
символов
приведен в
Приложение D:
Права
системного
приложения
Alpha.Security
(стр. 139) (см.
описание права
SpecialCount)
«true» – в
пароле
должен
содержаться
хотя бы один
специальный
символ;
«false» –
в пароле не
обязательно
использовать
специальные
символы.
<MinimalPasswordLength>
соответствует праву Минимальная
длина пароля
Требование к
количеству
символов в
пароле
Любое значение
типа int4.
Чтобы право не
добавлялось
автоматически при
создании новой учетной
записи, необходимо
указать значение «0».
Если уменьшить
значение, указанное в
файле, то у уже
существующих
пользователей будет
указано старое
значение права, но с
возможностью
уменьшить или
удалить это значение.
Если увеличить
значение, указанное в
файле, то у уже
существующих
пользователей в
качестве значения
права будет указано
новое значение из
файла.
<MinimalPasswordHistoryLength>
соответствует праву Количество
паролей в истории
Требование к
количеству
паролей,
хранимых в
истории
Любое значение
типа int4.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
97

=== Page 77 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
Элемент
На что влияет
Возможные
значения
Примечание
<IdentityConfirmation>
Параметр, регулирующий
необходимость подтверждения
личности при запуске конфигуратора
при наличии активной
пользовательской сессии
-
-
Описано в Подключение к
LDAP-серверу с помощью
агента безопасности (стр.
77)
ПРИМЕР
Если не менять файл, то при создании новой учетной записи права назначаются автоматически.
Выставим значения «false» и «0» у всех элементов для того, чтобы отключить автоматическое
назначение прав:
<?xml version="1.0" encoding="utf-8"?>
<Configuration ProductName="Alpha.SecurityConfigurator" ProductVersion="">
<Configurable Id="defaultPassReq">
<DefaultPasswordRequirementsSettings>
<DigitsRequired>false</DigitsRequired>
<UpperRequired>false</UpperRequired>
<LowerRequired>false</LowerRequired>
<SpecialRequired>false</SpecialRequired>
<MinimalPasswordLength>0</MinimalPasswordLength>
<MinimalPasswordHistoryLength>0</MinimalPasswordHistoryLength>
<IdentityConfirmation>true</IdentityConfirmation>
</DefaultPasswordRequirementsSettings>
</Configurable>
</Configuration>
Тогда при создании новой учетной записи ни одно право не будет добавлено автоматически:
98
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 78 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
6.6. Назначение и указание значений прав
Право может быть назначено:
пользователю лично – в окне редактирования учетной записи пользователя или в окне
редактирования прав;
группе пользователей – в окне редактирования группы или в окне редактирования прав;
роли – в разделе приложений.
При назначении права указывается значение права. Итоговое значение права для пользователя зависит от
того, какое значение права указано ему лично, в каких группах он состоит и какие роли ему назначены. Такое
значение называется эффективным значением права. Подробнее об этом в Получить эффективное
значение права (стр. 102).
Назначить право группе
Назначить право группе можно или в окне редактирования права, или в окне редактирования группы.
В окне редактирования права:
1. Нажмите Добавить значение. Появится строка с неопределенным значением права.
2. Выберите строку и нажмите Добавить группы. В диалоговом окне выберите нужные группы.
3. Укажите значение права для добавленной группы:
«разрешено» или «запрещено» – для логического права;
разрешающее значение и запрещающее значение – для строкового права.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
99

=== Page 79 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
В окне редактирования группы:
1. Нажмите Добавить права.
2. В диалоговом окне разверните приложение, права из которого необходимо назначить группе, и
выберите нужные права.
В редакторе группы появятся строки прав с неопределенными значениями.
ОБРАТИТЕ ВНИМАНИЕ
Приложение Alpha.Security – это системное приложение, оно содержит системные права. Их
можно назначить группе, например, чтобы разрешить просмотр и редактирование конфигурации
всем пользователям в группе. Подробнее каждое право описано в Приложение D: Права
системного приложения Alpha.Security (стр. 139).
Приложения Alpha.ClusterWorkPlaces и Alpha.WorkStations содержат права доступа к
кластерным рабочим местам и АРМ. Подробнее об их использовании читайте в 6.7. Организация
кластерного рабочего места (стр. 103).
3. Укажите значения добавленных прав для группы:
«разрешено» или «запрещено» – для логического права;
разрешающее значение и запрещающее значение – для строкового права.
ПРИМЕР
Для пробной конфигурации назначьте права группам и укажите значения следующим образом:
группе «Операторы» разрешен «Просмотр технологического процесса» и запрещено
«Управление технологическим процессом»;
группе «Диспетчеры» запрещен «Просмотр технологического процесса» и разрешено
«Управление технологическим процессом»;
значения прав для группы «Начальники участка» оставьте неопределенными.
100
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 80 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
Назначить право пользователю
Назначить право пользователю можно или в окне редактирования права, или в окне редактирования учетной
записи пользователя.
В окне редактирования права:
1. Нажмите Добавить значение. Появится строка с неопределенным значением права.
2. Выберите строку и нажмите Добавить пользователей. В диалоговом окне выберите нужных
пользователей.
3. Укажите значение права для добавленных пользователей:
«разрешено» или «запрещено» – для логического права;
разрешающее значение и запрещающее значение – для строкового права.
В окне редактирования учетной записи:
1. Нажмите Добавить права.
2. В диалоговом окне разверните приложение, права из которого необходимо назначить группе, и
выберите нужные права.
В редакторе учетной записи появятся строки прав с неопределенными значениями.
ОБРАТИТЕ ВНИМАНИЕ
Приложение Alpha.Security – это системное приложение, оно содержит системные права. Их
можно назначить пользователю, например, чтобы разрешить просмотр и редактирование
конфигурации, или ограничить длительность сессии пользователя. Подробнее каждое право
описано в Приложение D: Права системного приложения Alpha.Security (стр. 139).
О приложениях Alpha.ClusterWorkPlaces и Alpha.WorkStations и их использовании читайте в
6.7. Организация кластерного рабочего места (стр. 103).
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
101

=== Page 81 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
3. Укажите значения добавленных прав для группы:
«разрешено» или «запрещено» – для логического права;
разрешающее значение и запрещающее значение – для строкового права.
Получить эффективное значение права
Значение одного и того же права может быть назначено:
пользователю лично;
группе пользователей;
роли.
В зависимости от того, в какой группе состоит пользователь и какая роль ему назначена, зависит
эффективное значение права.
Правила определения эффективного значения права:
Для булевского права:
если есть хоть одно разрешающее значение и нет запрещающих, эффективное значение
разрешающее;
если есть хоть одно запрещающее значение, эффективное значение запрещающее.
Для строковых прав эффективное значение складывается из всех наследованных прав. Строковые
права отображаются списком.
Эффективные значения для системных прав Alpha.Security в Приложение D: Права системного
приложения Alpha.Security (стр. 139).
102
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 82 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
ПРИМЕР
Перейдите к редактированию учетной записи пользователя «Семенов Семен», состоящего в группе
«Начальники участка» и обладающего ролью «Начальник участка». Обратите внимание, что:
ни одно право не было назначено пользователю лично;
пользователь состоит в группе «Начальники участка», которой назначены оба права
приложения «Участок 1», но не указаны значения прав;
пользователю назначена роль «Начальник участка», обладающая разрешениями обоих прав
приложения «Участок 1».
В столбце Эффективное значение обоих прав – «разрешено», столбец Значение пустует.
Укажите группе «Начальники участка» запрещающее значение права «Просмотр технологического
процесса». Затем вернитесь к редактированию учетной записи начальника участка. Согласно правилу
определения эффективного значения права, пользователю будет запрещено наблюдать за
технологическим процессом.
Добавьте пользователю лично право «Управление технологическим процессом». В строке права
заполнится столбец Значение. Здесь можно указать значение права лично для пользователя.
6.7. Организация кластерного рабочего места
Несколько АРМ можно объединить в кластерное рабочее место. Тогда после входа с учетными данными на
одном АРМ, вход автоматически произойдет на остальных АРМ, входящих в кластерное рабочее место.
Чтобы создать кластерное рабочее место, необходимо:
1. Объединить АРМ, входящие в кластерное рабочее место, в сеть Alpha.Net.
2. Настроить Агент Alpha.Security всех АРМ на общий LDAP-сервер.
3. Создать кластерное рабочее место, используя SecurityConfigurator.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
103

=== Page 83 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
Когда кластерные рабочие места будут созданы, доступ к кластерным местам и АРМ можно будет
назначать пользователям и группам в виде прав приложений Alpha.ClusterWorkPlaces и
Alpha.WorkStations.
Объединить АРМ в сеть Alpha.Net
Перед началом настройки определите АРМ, который будет центральным узлом сети Alpha.Net: на
центральном узле сети создана нужная конфигурация LDAP-сервера (пользователи, группы, приложения и
права). Настройки центрального узла будут отличаться от настроек остальных АРМ.
ОБРАТИТЕ ВНИМАНИЕ
Ниже описано создание простейшей сети Alpha.Net, в которой все узлы соединяются с центральным
узлом сети. Более сложные схемы сети Alpha.Net следует использовать только если центральный
узел сети не имеет сетевого соединения с каким-либо другим узлом (например, если компьютеры
находятся в разных сетях, между которыми работает брандмауэр). В данном примере такие схемы
не рассматриваются.
На каждом АРМ:
1. Установите Alpha.Net (входит в дистрибутив Alpha.Domain).
2. Сконфигурируйте Alpha.Net:
2.1. Перейдите в папку установки C:\Program Files\Automiq\Alpha.Domain и откройте файл
конфигурации alpha.net.agent.xml в любом текстовом редакторе.
2.2. В атрибутах элемента Alpha.Net.Agent укажите параметры АРМ в сети Alpha.Net.
Атрибут
Описание
Name
Имя АРМ в сети Alpha.Net. Должно быть уникальным в сети Alpha.Net.
NetEnterPort
Порт, по которому другие службы соединяются с данным узлом (по умолчанию
– «1010»).
ParentAgentPort
Порт для соединения с центральным узлом сети Alpha.Net.
Рекомендуется разным узлам назначать разные значения атрибута.
У центрального узла сети указывать не обязательно.
ПРИМЕР
Центральный узел:
<Alpha.Net.Agent Name="CentralNode" NetEnterPort="1010" >
Остальные АРМ в сети:
<Alpha.Net.Agent Name="ARM1" NetEnterPort="1010"
ParentAgentPort="1009">
<Alpha.Net.Agent Name="ARM2" NetEnterPort="1010"
ParentAgentPort="1090">
104
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 84 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
2.3. На центральном узле сети Alpha.Net, в этом же файле, раскомментируйте конструкцию
<ChildAgents> и перечислите все дочерние узлы сети, указав их параметры:
Атрибут
Описание
Name
Имя дочернего узла сети Alpha.Net. Указано в конфигурации дочернего узла в атрибуте
Name.
Address
IP-адрес дочернего узла сети Alpha.Net.
Port
Номер порта для подключения к дочернему узлу. Указан в конфигурации дочернего
узла в атрибуте ParentAgentPort.
ПРИМЕР
<Alpha.Net.Agent Name="CentralNode" NetEnterPort="1010" >
<ChildAgents>
<ChildAgent Name="ARM1" Address="199.99.99.101" Port="1009"/>
<ChildAgent Name="ARM2" Address="199.99.99.102" Port="1090"/>
</ChildAgents>
<Options LoggerLevel="2"/>
</Alpha.Net.Agent>
2.4. Перезапустите службу Alpha.Net.Agent, чтобы применить внесённые изменения.
В результате АРМ будут объединены в сеть Alpha.Net.
Настроить Агент Alpha.Security на общий LDAP-сервер
На всех АРМ сети должен быть установлен Alpha.Security. При этом каждый Агент Alpha.Security должен
быть настроен на один и тот же каталог LDAP-сервера центрального узла.
На каждом дочернем узле сети:
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
105

=== Page 85 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
1. Установите Alpha.Security;
2. Перейдите к настройке Агент Alpha.Security. Откройте конфигурационный файл
alpha.security.agent.xml, расположенный в C:\Program Files\Automiq\Alpha.Security и укажите:
2.1. Параметры локальной точки доступа Net-агента, входящей в сеть Alpha.Net:
ПРИМЕР
<EntryPointNetAgent Address="127.0.0.1" Port="1010"/>
2.2. Параметры LDAP-сервера, развернутого на центральном узле сети:
ПРИМЕР
<LdapHosts>
<LDAPServer Address="199.99.99.111" Port="389"/>
</LdapHosts>
2.3. Администратора LDAP, пароль администратора и корневой каталог – такие же, как в настройках
Агент Alpha.Security на центральном узле сети.
ПРИМЕР
<!-- Каталог пользователя LDAP -->
<LdapUser value="cn=Manager,dc=maxcrc,dc=com"/>
<!-- Пароль LDAP -->
<LdapPassword value="..."/>
<!-- Корневой каталог -->
<SecurityDn value="ou=Security,dc=maxcrc,dc=com"/>
3. Перезапустите службу Alpha.Security.Agent, чтобы применить внесённые изменения.
В результате АРМ сети будут настроены на общий LDAP-сервер.
Создать кластерное рабочее место
Кластерное рабочее место создаётся в SecurityConfigurator:
1. На панели инструментов выберите Рабочие места.
106
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 86 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
2. Добавьте кластерное рабочее место.
3. Для каждого АРМ, который войдёт в кластерное рабочее место, добавьте рабочую станцию и укажите
свойства.
Параметр
Описание
Имя рабочей станции
Произвольное имя.
Идентификатор рабочей
станции
Имя АРМа в сети Alpha.Net. Совпадает со значением атрибута Name в
файле конфигурации Alpha.Net.
Имя кластерного
рабочего места
Выберите кластерное рабочее место, добавленное ранее.
Свойства
В результате будет создано кластерное рабочее место, в которое входят АРМ из числа объединенных в сеть
Alpha.Net.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
107

=== Page 87 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
Предоставить доступ к кластерным рабочим местам и АРМ пользователям
Права доступа к созданным кластерным рабочим местам и АРМ хранятся в приложениях
Alpha.ClusterWorkPlaces и Alpha.WorkStations соответственно. Права создаются автоматически в момент
создания соответствующих элементов.
Назначить права доступа можно как пользователям, так и группам:
Разрешен доступ к рабочему месту – право доступа к кластерному рабочему месту.
Разрешен доступ к рабочей станции – право доступа к отдельному АРМ.
В результате возможность авторизоваться на всех АРМ, входящих в кластерное рабочее место, зависит от
комбинации назначенных прав.
Доступ к
кластерному
рабочему месту
Доступ к АРМ,
входящим в кластерное
рабочее место
Результат авторизации
Есть
Есть, ко всем
При входе на одном из АРМ авторизация происходит на
всех АРМ, входящих в кластерное рабочее место.
Есть, не ко всем
При входе на одном из АРМ, к которому есть
доступ, авторизация происходит только на тех АРМ, к
которым имеется доступ.
Нет
Есть
При входе на одном из АРМ не происходит авторизация на
остальных АРМ.
6.8. Резервное копирование конфигурации
Информацию из каталогов LDAP можно сохранять в резервные копии. Они могут пригодиться при переносе
конфигурации на другие АРМ, для создания отчетов и пр. Используйте SecurityConfigurator для создания
резервных копий. Способы создания и варианты использования копий описаны в таблице ниже.
108
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 88 ===
6. РЕДАКТИРОВАНИЕ КОНФИГУРАЦИИ НА LDAP-СЕРВЕРЕ С ПОМОЩЬЮ SECURITYCONFIGURATOR
Что сохранить
Формат
файла
Как сохранить
Как использовать
Полная резервная
копия конфигурации
*.bak
Меню -> Сохранить
резервную копию
Можно восстановить конфигурацию из
резервной копии:
Меню -> Восстановить из резервной копию
Список приложений и
прав
*.xml
Раздел Приложения ->
Сохранить в файл
Можно импортировать приложения и права из
сохраненного файла:
Приложения -> Добавить из файла
*.xlsx
*.csv
*.docs
Раздел Приложения ->
Экспорт в Excel
В качестве отчета о разрешениях и запретах
пользователей и групп пользователей
Список
пользователей
*.xlsx
*.xml
*.csv
*.docs
Раздел Приложения ->
Экспорт в Excel
Во всех случаях, когда нужен список
пользователей со всеми данными
пользователей
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
109

=== Page 89 ===
7. АУДИТ БЕЗОПАСНОСТИ
7. Аудит безопасности
Alpha.Security отправляет сообщения о любых изменениях в подсистеме безопасности. Эта функция
называется аудитом безопасности.
По умолчанию Агент Alpha.Security транслирует сообщения, однако их получение необходимо настраивать,
как описано в данном разделе. Можно настроить запись сообщений аудита в сигналы Alpha.Server и, при
необходимости, в журнал приложений. Чтобы получать сообщения о состоянии подсистемы безопасности в
сигналы Alpha.Server, необходимо:
настроить Агент Alpha.Security, при необходимости изменив тексты сообщений;
подготовить сигналы в Alpha.Server, подключить к серверу модуль OPC AE Server (он записывает
сообщения в сигналы).
Как полностью отключить трансляцию любых сообщений аудита, описано в подразделе Отключение аудита
безопасности (стр. 118).
О типах сообщений
Сообщения, транслируемые агентом безопасности, делятся на три типа:
первые сообщают об изменениях в списках пользователей, групп и приложений, в т.ч. прав и ролей;
вторые – служебные сообщения о работе Агент Alpha.Security (вход и выход пользователя,
выполнение контроля целостности и пр.);
третьи хранят информацию о текущем пользователе (логин, отображаемое имя, группа) и рабочей
станции.
Чтобы ознакомиться с сообщениями первых двух типов, перейдите к файлу alpha.security.agent.json,
расположенному в:
C:\Program Files\Automiq\Alpha.Security – для ОС Windows;
/opt/Automiq/Alpha.Security – для ОС Linux.
Сообщениями третьего типа являются:
логин текущего пользователя;
отображаемое имя текущего пользователя;
название группы, в которой состоит текущий пользователь;
имя текущей рабочей станции.
Настройка Агент Alpha.Security и редактирование текстов сообщений
Для настройки трансляции сообщений следует редактировать конфигурационный файл
alpha.security.agent.xml, для редактирования сообщений – файл alpha.security.agent.json. Оба
файла расположены в:
C:\Program Files\Automiq\Alpha.Security – для ОС Windows;
/opt/Automiq/Alpha.Security – для ОС Linux.
110
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 90 ===
7. АУДИТ БЕЗОПАСНОСТИ
Редактирование шаблонов текстов сообщений
Файл alpha.security.agent.json хранит шаблоны текстов сообщений, которые можно редактировать. При
формировании шаблона текста сообщения можно использовать теги. Теги описаны в начале файла. Для
каждого шаблона указаны параметры, назначение которых описано в таблице ниже.
Расшифровка текстов сообщений для упрощения их понимания приведена в приложении Приложение E:
Сообщения аудита (стр. 144).
Название
параметра
Назначение параметра
name
Идентификатор сообщения. Менять нельзя.
value
Текст сообщения.
type
Тип сообщения. Тип служит для пометки сообщений, которые могут быть записаны в один
и тот же сигнал Alpha.Server.
По умолчанию все сообщения имеют тип Admin и записываются в один и тот же сигнал,
указанный в карте сигналов конфигурационного файла alpha.security.agent.xml. Чтобы
разные сообщения записывались в разные сигналы, одним сообщениям необходимо
указать тип Admin, а другим – Normal, а затем в карте сигналов указать эти типы для
разных сигналов.
Названия Admin и Normal можно менять, главное – чтобы новые названия были указаны в
обоих конфигурационных файлах.
severity
Категория важности сообщения. Этот параметр служит для разделения всех сообщений на
четыре категории важности. Категории описаны в карте важности конфигурационного
файла alpha.security.agent.xml. По умолчанию для всех сообщений указана категория
важности Info.
sound
Звук, который должен быть воспроизведен при наступлении события, о котором говорится
в сообщении. Формат значения – имя и расширение файла звука. Файл звука должен
находиться в папке проекта, посредством которого просматриваются события, например,
Alpha.HMI.Alarms. Подробнее об этом – в документе на соответствующий продукт.
ackrequired
Необходимость квитирования события, о котором говорится в сообщении. Если
необходимо квитировать событие, укажите значение «1», если нет – «0».
ПРИМЕР
По умолчанию сообщение описано следующим образом:
{"name":"AUDIT_ADD_USER", "value":"На '%arm.name%' от имени
'%currUser.symbolicId%' группа '%currGroup.symbolicId%': Настройка списка
пользователей - Добавлен пользователь '#user.displayName#'.", "type":"Admin",
"severity":"Info", "sound":"", "ackrequired":"0"}
Здесь можно изменить текст сообщения, тип и важность, указать звук и необходимость
квитирования:
{"name":"AUDIT_ADD_USER", "value":"В группу '%currGroup.symbolicId%' добавлен
пользователь '#user.displayName#'.", "type":"Normal", "severity":"Debug",
"sound":"defaul.wav", "ackrequired":"1"}
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
111

=== Page 91 ===
7. АУДИТ БЕЗОПАСНОСТИ
ПРИМЕЧАНИЕ
Сообщения первого типа отправляются в результате изменений, произведенных в конфигураторе
безопасности.
Alpha.HMI.SecurityConfigurator транслирует сообщения аудита первого типа, перечисленные
в alpha.security.agent.json.
SecurityConfigurator транслирует собственные сообщения аудита первого типа, поэтому
изменить их не получится.
Чтобы пользоваться функцией аудита безопасности, включите в настройках SecurityConfigurator
подключение к агенту безопасности.
Настройка агента безопасности
Файл alpha.security.agent.xml позволяет настроить трансляцию сообщений аудита. Для этого:
1. Откройте файл. Перейдите к элементу <AuditLogConsumers>.
Чтобы сообщения помимо сигналов Alpha.Server транслировались в журнал приложений, задайте
значение атрибута TraceAudit:
«1» – для включения трансляции сообщений в журнал приложений;
«0» – для отключения трансляции сообщений в журнал приложений.
<AuditLogConsumers TraceAudit="1">
ПРИМЕЧАНИЕ
Если настроить трансляцию только в сигналы сервера (TraceAudit="0"), с сообщениями
можно будет ознакомиться в любом приложении для просмотра значений сигналов или в
Alpha.HMI.Alarms. Если настроить трансляцию в журнал приложений (TraceAudit="1"), то для
его просмотра можно будет использовать Alpha.HMI.SystemLogViewer или EventLogViewer.
112
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 92 ===
7. АУДИТ БЕЗОПАСНОСТИ
2. Во вложенном элементе <OpcDaLogConsumer> опишите так называемый сервер-потребитель
сообщений – экземпляр Alpha.Server, в сигналы которого будут транслироваться сообщения. Укажите
значения атрибутов элемента <Server>:
Host – IP-адрес сервера;
Type – тип сервера («OPC» или «TCP» для Windows, только «TCP» для Linux);
ProgId – строковый идентификатор OPC-сервера (если выбран OPC-сервер);
TCPServerPort – порт для подключения к TCP-серверу (если выбран TCP-сервер);
HostTcpReserve – имя или IP-адрес сервера для резервного канала связи с TCP-сервером
(значение может быть пустым);
MasterPasswordCipher – хэш-значение мастер-пароля, установленного на подключение к TCP-
серверу (значение может быть пустым).
ПРИМЕЧАНИЕ
Это значение должно совпадать со значением атрибута Cipher элемента
<MasterPassword> в файле настроек Alpha.Server или Alpha.AccessPoint:
<MasterPassword Cipher="bknxu/rPt/+PCnmzYA....lB1i2bHuzYk2/XKKYFr" />
<Server Host="127.0.0.1" Type="OPC" ProgId="AP.OPCDAServer"
TCPServerPort="4388"
HostTcpReserve="" MasterPasswordCipher="">
ОБРАТИТЕ ВНИМАНИЕ
В рамках одного элемента <OpcDaLogConsumer> может быть настроен только один сервер-
потребитель сообщений.
Количество элементов <OpcDaLogConsumer> может быть любым.
3. Задайте значения для каждой категории важности событий в карте важности <SeverityMap>,
изменив значения атрибутов Value. Атрибут может принимать значения от 0 до 999. Обратите внимание,
что эти значения понадобятся в дальнейшем – например, при настройке событий в сигналах
Alpha.Server, при настройке отображения событий в Alpha.HMI.Alarms.
Таким образом можно отметить, какие сообщения имеют высокую важность, а какие – низкую. По
умолчанию всем сообщениям в файле alpha.security.agent.json указана категория важности «Info».
<SeverityMap>
<Severity Category="Critical" Value="800" Sound=""/>
<Severity Category="Important" Value="200" Sound=""/>
<Severity Category="Info" Value="100" Sound=""/>
<Severity Category="Debug" Value="0" Sound=""/>
</SeverityMap>
Здесь же для каждой категории в качестве значения атрибута Sound можно указать файл звука, который
должен быть воспроизведен при наступлении события из этой категории. Звук может быть указан либо
для категории важности, либо для каждого сообщения о событии отдельно – в файле
alpha.security.agent.json, как описано выше. Если для сообщения не указан звук, то при наступлении
события воспроизводится звук, указанный для категории важности этого события. Файл звука должен
находиться в папке проекта, посредством которого просматриваются события, например,
Alpha.HMI.Alarms. Подробнее об этом – в документе на соответствующий продукт.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
113

=== Page 93 ===
7. АУДИТ БЕЗОПАСНОСТИ
4. Заполните значения атрибутов карты сигналов <SignalMap>. В указанные здесь сигналы и
записываются сообщения аудита. Обратите внимание, что названия сигналов могут быть любыми.
Важно, чтобы для каждого типа – Normal, Admin, UserName, DisplayName, GroupName и
WorkstationName – было создано по два сигнала с разным режимом записи. Подробнее назначения
атрибутов карты описаны в таблице ниже.
<SignalMap>
<Signal Name="DynEvents.NormalDynSignal" Mode="DynamicEvent" Type="Normal"/>
<Signal Name="DynEvents.AdminDynSignal" Mode="DynamicEvent" Type="Admin"/>
<Signal Name="DynEvents.UserNameDynSignal" Mode="DynamicEvent"
Type="UserName"/>
<Signal Name="DynEvents.DisplayNameDynSignal" Mode="DynamicEvent"
Type="DisplayName"/>
<Signal Name="DynEvents.GroupNameDynSignal" Mode="DynamicEvent"
Type="GroupName"/>
<Signal Name="DynEvents.WorkstationNameDynSignal" Mode="DynamicEvent"
Type="WorkstationName"/>
<Signal Name="DynEvents.NormalMessage" Mode="Value" Type="Normal"/>
<Signal Name="DynEvents.AdminMessage" Mode="Value" Type="Admin"/>
<Signal Name="DynEvents.UserNameMessage" Mode="Value" Type="UserName"/>
<Signal Name="DynEvents.DisplayNameMessage" Mode="Value"
Type="DisplayName"/>
<Signal Name="DynEvents.GroupNameMessage" Mode="Value" Type="GroupName"/>
<Signal Name="DynEvents.WorkstationNameMessage" Mode="Value"
Type="WorkstationName"/>
</SignalMap>
Название
атрибута
Назначение атрибута
Name
Полное имя сигнала как в Alpha.Server.
Mode
Режим записи сообщения в сигнал:
«DynamicEvent» – сигнал, создающий динамическое событие;
«Value» – обычная запись сообщения.
Type
Тип сообщений, записывающихся в сигнал. Типы описаны в начале данного раздела.
Для каждого сообщения третьего типа (UserName, DisplayName, GroupName и
WorkstationName) создается по собственной паре сигналов.
Для сообщений первого и второго типа достаточно двух пар сигналов. В этом случае
атрибут Type служит для пометки сообщений, которые могут быть записаны в один и тот
же сигнал. По умолчанию в файле alpha.security.agent.json все сообщения имеют тип
Admin, и записываются в один и тот же сигнал, указанный в карте сигналов. Чтобы разные
сообщения записывались в разные сигналы, одним сообщениям необходимо указать тип
Admin, а другим – Normal, а затем в карте сигналов указать эти типы для разных пар
сигналов. Названия Admin и Normal можно менять, главное – чтобы новые названия были
указаны в обоих конфигурационных файлах.
Назначения атрибутов карты сигналов
5. Дополнительно можно изменить префикс сообщений аудита, изменив значение атрибута value
элемента <mesPrefix>. Он служит для выделения сообщений аудита безопасности в списке всех
остальных сообщений, которые могут отображаться в средстве просмотра.
114
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 94 ===
7. АУДИТ БЕЗОПАСНОСТИ
Подготовка сигналов в Alpha.Server
Для каждого сообщения аудита необходимо создать по два сигнала: обычный и динамический.
Динамический сигнал позволяет сгенерировать событие, отправляющее сообщение из обычного сигнала в
средства просмотра сообщений.
Чтобы подготовить Alpha.Server к записи сообщений подсистемы безопасности, необходимо создать 12
сигналов типа String в отдельной папке дерева сигналов. Имена сигналов по умолчанию перечислены в
конфигурационном файле alpha.security.agent.xml, но их можно изменить.
Динамические сигналы, приведенные в конфигурационном файле по умолчанию:
DynEvents.NormalDynSignal;
DynEvents.AdminDynSignal;
DynEvents.UserNameDynSignal;
DynEvents.DisplayNameDynSignal;
DynEvents.GroupNameDynSignal;
DynEvents.WorkstationNameDynSignal.
Обычные сигналы, приведенные в конфигурационном файле по умолчанию:
DynEvents.NormalMessage;
DynEvents.AdminMessage;
DynEvents.UserNameMessage;
DynEvents.DisplayNameMessage;
DynEvents.GroupNameMessage;
DynEvents.WorkstationNameMessage.
Создание сигналов в приложении Конфигуратор
Если для конфигурирования Alpha.Server вы используете приложение Конфигуратор, то:
1. Создайте в дереве сигналов папку для сигналов аудита (например DynEvents). Внутри папки создайте
12 сигналов типа String.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
115

=== Page 95 ===
7. АУДИТ БЕЗОПАСНОСТИ
2. Затем настройте генерацию событий при записи сообщений в сигналы. Для этого назначьте созданным
объектам свойства, описанные в таблицах ниже. Также можно включить флаг ведения истории, чтобы
иметь возможность обратиться к ней при перезаписи значения сигнала.
ПРИМЕЧАНИЕ
Для того, чтобы запись сообщения в сигнал генерировала событие, в конфигурацию
Alpha.Server должен быть включен модуль OPC AE Server. Подробнее о том, как подключить,
настроить и использовать модуль, читайте в соответствующем документе.
Папке DynEvents:
Свойство
Значение
999000 (тип
объекта)
Можно не указывать.
999004
(условие
генерации
сообщений)
Cкрипт, генерирующий сообщение при наступлении события.
ПРИМЕР
<EventConditions>
<EventCondition Name="DynamicCondition"
Type="Dynamic" Enabled="1">
<Subcondition Type="Dynamic" Message="" Value=""
Sound="" Severity="100"
AckRequired="0" Enabled="1" SoundEnabled="0" />
</EventCondition>
</EventConditions>
где:
значение атрибута Name будет использоваться при настройке
динамических сигналов;
значение атрибута Severity должно совпадать со значением
категории важности сообщений, записывающихся в сигнал,
указанным при настройке агента.
Динамическим сигналам (содержат частицу «Dyn» в названии по умолчанию):
Свойство
Значение
5000 (адрес
сигнала)
Conditions=(DynamicCondition),
где название условия в скобках должно совпадать со значением атрибута
Name, указанным в свойстве 999004 папки DynEvents.
9001 (флаг
ведения истории)
True
Обычным сигналам:
Свойство
Значение
9001 (флаг ведения истории)
True
116
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 96 ===
7. АУДИТ БЕЗОПАСНОСТИ
Создание сигналов в Alpha.DevStudio
ПРИМЕЧАНИЕ
Порядок создания проекта и конфигурирования Alpha.Server описаны в документации на
Alpha.DevStudio (раздел «Знакомство с Alpha.DevStudio руководства пользователя»). Здесь
описано создание сигналов в уже сконфигурированном Alpha.Server в существующем проекте.
Если для конфигурирования Alpha.Server вы используете Alpha.DevStudio, то:
1. Откройте имеющийся проект Alpha.DevStudio. Перейдите к элементу, описывающему сервер в вашем
проекте. Убедитесь, что здесь подключен элемент OPC AE Server.
2. Перейдите внутрь элемента, описывающего сервер. Здесь может быть размещен элемент
приложения. Если его нет, создайте, перетянув элемент Приложение с панели элементов.
3. Внутри элемента приложения создайте логический объект. Это будет папка для сигналов,
предназначенных для записи сообщений аудита (например DynEvents).
4. Внутри созданного логического объекта создайте двенадцать параметров, соответствующих
двенадцати сигналам, предназначенным для записи сообщений аудита. Для всех параметров укажите
значения свойств:
Направление («отсутсвует»);
Тип («string»);
Имя.
5. Для шести параметров, предназначенных для создания динамических событий, в окне События
установите флаг Генерировать события (такие сигналы в именах по умолчанию содержат частицу «Dyn»).
Чтобы открыть окно, перейдите к панели инструментов и выберите Вид -> События. В открывшейся
таблице укажите значение важности события, соответствующее категории важности, указанной при
конфигурировании агента. Если необходимо, укажите файл звука, воспроизводимого при наступлении
события, и параметры квитирования.
6. Постройте решение и примените конфигурацию. Чтобы убедиться, что сигналы созданы в сервере,
откройте приложение Конфигуратор или OpcExplorer и проверьте, что созданная папка с сигналами
появилась в дереве сигналов.
Получение сообщений аудита
После внесения изменений в конфигурации сервера и агента безопасности, перезапустите их службы
(сервисы). В результате будет настроена трансляция сообщений аудита в сигналы Alpha.Server и в журнал
приложений (если настраивали). Чтобы ознакомиться с сообщениями, используйте любое средство
просмотра значений сигналов сервера либо приложение Alpha.HMI.Alarms. Если также настраивали
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
117

=== Page 97 ===
7. АУДИТ БЕЗОПАСНОСТИ
трансляцию сообщений в журнал приложений, просмотреть его можно в приложениях EventLogViewer и
Alpha.HMI.SystemLogViewer.
Для примера ниже приведено изображение окна приложения Alpha.HMI.Alarms. Внесите изменения в
конфигурацию Alpha.Security: укажите номер телефона существующего пользователя или создайте новую
учетную запись. Сообщения о внесенных изменениях появятся в окне Alpha.HMI.Alarms.
Отключение аудита безопасности
Чтобы полностью отключить трансляцию сообщений аудита, закомментируйте или полностью удалите
элемент <AuditLogConsumers> в конфигурационном файле alpha.security.agent.xml. Трансляция
сообщений не будет выполняться, однако при каждом перезапуске агента безопасности в журнале
приложений будет появляться одно сообщение с текстом Аудит недоступен: параметры аудита не
определены в конфигурации Security-агента (элемент AuditLogConsumers).
118
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 98 ===
8. КОНТРОЛЬ ЦЕЛОСТНОСТИ ФАЙЛОВ И ПАПОК
8. Контроль целостности файлов и папок
Подсистема Alpha.Security позволяет проводить проверку состояния файлов и папок на текущем
компьютере. При выполнении проверки текущее состояние файлов сравнивается с ожидаемым состоянием.
Ожидаемое состояние называется эталоном.
По умолчанию контроль целостности включен и выполняется для некоторых системных файлов и папок.
Сообщения о результатах проверок записываются в журнал приложений, ознакомиться с которым можно с
помощью приложений Alpha.HMI.SystemLogViewer или EventLogViewer. Как отключить контроль
целостности, описано ниже.
Чтобы изменить настройки контроля целостности, можно:
использовать приложение Alpha.HMI.IntegrityControl версии 2.4.1 и новее.
создать собственное приложение для конфигурирования контроля целостности. Для этого создайте
проект Alpha.HMI, использующий расширение Alpha.HMI.Security версии 2.0.11 и новее. Расширение
предоставит компонент Настройка безопасности: Контроль целостности, позволяющий управлять
настройками контроля целостности. Подробнее об этом – в документации на Alpha.HMI.Security.
ОБРАТИТЕ ВНИМАНИЕ
Такая настройка контроля целостности выполняется для Alpha.Security версии 1.7.24 и новее. Ранее
настройка выполнялась с помощью файлов alpha.security.agent.xml и alpha.security.ic.xml,
расположенных в:
C:\Program Files\Automiq\Alpha.Security – для ОС Windows;
/opt/Automiq/Alpha.Security – для ОС Linux.
Если на вашем компьютере ранее был настроен контроль целостности, то при установке
Alpha.Security версии 1.7.24 и новее разработанная в более ранних версиях конфигурация контроля
целостности автоматически преобразуется в новый формат. Полученная конфигурация сохранится в
виде зашифрованных файлов в папке:
C:\Program Files\Automiq\Alpha.Security\IC на ОС Windows;
/opt/Automiq/Alpha.Security/IC на ОС Linux.
Отдельная конфигурация хранится в виде отдельного файла и представляет собой так называемую
группу контроля целостности. Агент безопасности может хранить несколько групп одновременно,
однако активна может быть только одна из них. Настройки каждой группы можно менять отдельно.
Отключение и включение контроля целостности
Чтобы полностью отключить контроль целостности, удалите файл alpha.security.ic.xml и папку IC,
расположенные в:
C:\Program Files\Automiq\Alpha.Security – для ОС Windows;
/opt/Automiq/Alpha.Security – для ОС Linux.
После полного отключения заново включить контроль целостности может только пользователь, имеющий
права на просмотр и изменение конфигурации (ViewConfiguration и ConfigurationAccess), в приложении
Alpha.HMI.IntegrityControl. Для этого ему достаточно перейти к конфигурированию контроля целостности в
окне приложения и создать новую активную группу контроля целостности.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
119

=== Page 99 ===
9. БЕЗОПАСНОСТЬ В КОМПОНЕНТАХ АЛЬФА ПЛАТФОРМЫ
9. Безопасность в компонентах Альфа платформы
Подсистема безопасности Alpha.Security позволяет разграничивать возможности пользователей в
компонентах Альфа платформы. Например, сервис безопасности можно использовать в Alpha.HMI.Alarms
(Alpha.Alarms), Alpha.HMI.Trends (Alpha.Trends). Подробнее о том, как активировать сервис безопасности,
читайте в документах на соответствующие компоненты.
После того, как сервис безопасности активирован, необходимо назначить пользователям права на
использование возможностей компонентов. Для этого необходимы приложения, содержащие эти права.
Создавать приложения не нужно, используйте шаблоны приложений:
«Alarms» для компонентов Alpha.Alarms и Alpha.HMI.Alarms;
«Trends» для компонентов Alpha.Trends и Alpha.HMI.Trends.
ПРИМЕЧАНИЕ
Больше шаблонов приложений для различных компонентов Альфа платформы предоставляет
Alpha.HMI.SecurityConfigurator.
Шаблоны поставляются вместе с дистрибутивом Alpha.Security и находятся в папке:
C:\Program Files\Automiq\Alpha.Security\Configurator\Templates или C:\Program Files
(x86)\Automiq\Alpha.Security\Configurator\Templates для ОС Windows;
/opt/Automiq/Alpha.Security/Configurator/Templates для ОС Linux.
Чтобы использовать приложения в своих проектах, импортируйте приложения в конфигурацию
Alpha.Security. Для этого откройте окно редактирования приложений и нажмите Добавить из файла.
Перейдите к папке с шаблонами приложений и выберите нужный шаблон. Выбранное приложение появится в
списке приложений и будет содержать права на использование возможностей компонента. Подробнее каждое
право описано в документе на соответствующий продукт.
120
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 100 ===
9. БЕЗОПАСНОСТЬ В КОМПОНЕНТАХ АЛЬФА ПЛАТФОРМЫ
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
121

=== Page 101 ===
10. РЕШЕНИЕ РАСПРОСТРАНЕННЫХ ПРОБЛЕМ
10. Решение распространенных проблем
В разделе представлены инструкции по устранению проблем, возникающих при настройке компонентов
Alpha.Security, при редактировании конфигурации на LDAP-сервере с помощью SecurityConfigurator, и в
процессе работы подсистемы безопасности в целом. Раздел находится в разработке и будет дополняться.
Подзаголовки раздела совпадают с текстами ошибок:
в журнале приложений Windows;
в приложении EventLogViewer;
в диалоговых окнах приложения SecurityConfigurator.
Ошибки в системных журналах или в EventLogViewer
Служба 'SECURITYAGENT' не зарегистрирована
Эта ошибка возникает в тех случаях, когда Агент Alpha.Security не может запуститься. При этом служба
Alpha.Security.Agent (alpha.security.service) может находиться в статусе "выполняется". В таких
случаях в первую очередь стоит проверить, что конфигурационный файл alpha.security.agent.xml
составлен правильно. Пример конфигурационного файла находится в Приложение A: Пример
конфигурационного файла Агент Alpha.Security (стр. 131).
Ошибка при подключении к LDAP-серверу 'x.x.x.x:x'. Операция не удалась. Код
ошибки: 34
В конфигурационном файле alpha.security.agent.xml каталог администратора LDAP указан в
неправильном формате. Используйте формат указания каталогов, принятый для OpenLDAP: «cn="логин-
администратора",dc="домен-базы-данных"».
ПРИМЕР
Неправильно: <LdapUser value="Manager"/>
Правильно: <LdapUser value="cn=Manager,dc=maxcrc,dc=com"/>
Ошибка при подключении к LDAP-серверу 'x.x.x.x:x'. Неверное имя
пользователя или пароль
В конфигурационном файле alpha.security.agent.xml указан неверный каталог администратора LDAP.
Каталог администратора LDAP зачастую создается на этапе установки OpenLDAP. Не меняйте значение,
указанное в конфигурационном файле:
для ОС Windows – <LdapUser value="cn=Manager,dc=maxcrc,dc=com"/>;
для ОС Linux – <LdapUser value="cn=admin,dc=maxcrc,dc=com"/>.
Неправильный пароль для подключения к LDAP / Ошибка с кодом 53
Если пароль указан верно, а ошибка все равно возникает – убедитесь, что пароль указан в зашифрованном
виде, например:
122
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 102 ===
10. РЕШЕНИЕ РАСПРОСТРАНЕННЫХ ПРОБЛЕМ
<LdapPassword value="U7y9IEVgu3Bg++VKHxkRv4baTM6CKpuosNlqFNVJs2GVYIBKHCyx
/9omgL3DJigUPjFmX10FoNRYPeg3ycHSYLBDlOn7XXJewvulXD837Y8aQbOBfxU35AowqUR+8
yjFYFqFPxn7/fpIheuz6iuot9cJvqtrOyiMgHkFuOiRIOE"/>
Чтобы зашифровать пароль, используйте приложение alpha.security.crypter.exe, расположенное в
C:\Program Files\Automiq\Alpha.Security\Utils. Подробнее – в разделе 4. Агент безопасности и его
настройка (стр. 64), в пункте Указать администратора LDAP.
Сообщения вида "<= mdb_equality_candidates: (xxx) not indexed"
Сообщения появляются в системном журнале Linux, когда OpenLDAP не индексирует указанный атрибут
(xxx) для более быстрого поиска. Чтобы устранить эту проблему, необходимо присвоить индекс следующим
образом:
1. В любом месте создайте файл filename.ldif со следующим содержимым:
dn: olcDatabase={1}mdb,cn=config
changetype: modify
add: olcDbIndex
olcDbIndex: xxx eq
где вместо xxx следует указать атрибут из текста сообщения. Если сообщения возникают для разных
атрибутов, каждый из них можно перечислить в отдельной строке вида olcDbIndex: xxx eq. Пример:
dn: olcDatabase={1}mdb,cn=config
changetype: modify
add: olcDbIndex
olcDbIndex: AQRef eq
olcDbIndex: AQMemberID eq
olcDbIndex: AQMemberRole eq
2. Примените созданный файл с помощью команды:
sudo ldapadd -Y EXTERNAL -H ldapi:/// -f filename.ldif
Не удалось отправить сообщение потребителю (сработало исключение ...)
Сообщение появляется в результате каждой неуспешной попытки агента безопасности записать сообщение
аудита в сигнал Alpha.Server. Перепроверьте настройки аудита, описанные в разделе 7. Аудит безопасности
(стр. 110). Убедитесь в том, что в файле alpha.security.agent.xml:
в карте сигналов <SignalMap> перечислены сигналы, существующие в текущей конфигурации
Alpha.Server;
в атрибутах элемента <Server> описан модуль-потребитель сообщений, подключенный к
Alpha.Server.
Функцию аудита безопасности можно вовсе отключить, как – описано в разделе 7. Аудит безопасности (стр.
110).
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
123

=== Page 103 ===
10. РЕШЕНИЕ РАСПРОСТРАНЕННЫХ ПРОБЛЕМ
AP протокол: Не удалось получить ни одного активного подключенного
соединения с сервером
Ошибка возникает в результате некорректной настройки аудита безопасности (стр. 110), когда неверно
указан IP-адрес или порт Alpha.Server в файле alpha.security.agent.xml. Убедитесь, что IP-адрес, порт и
тип сервера-потребителя сообщений указаны верно.
Функцию аудита безопасности можно вовсе отключить, как – описано в разделе 7. Аудит безопасности (стр.
110).
Не удалось отправить уведомление об изменении конфигурации подписчику
Ошибка возникает в результате некорректной настройки аудита безопасности (стр. 110), когда неверно
сформирована карта сигналов <SignalMap>.
Функцию аудита безопасности можно вовсе отключить, как – описано в разделе 7. Аудит безопасности (стр.
110).
Ошибки в диалоговых окнах приложения SecurityConfigurator
Не удалось сохранить изменения на сервере: no write access to parent. У
пользователя недостаточно прав
Встречается при подключении из SecurityConfigurator, установленного на Windows, к OpenLDAP,
установленному на Linux. Ошибка возникает, если не были прописаны политики контроля доступа при
настройке OpenLDAP. Вернитесь к настройке LDAP-сервера: шаблон политик контроля доступа и примените
его.
objectClass: value #2 invalid per syntax. Неверный синтаксис
Ошибка возникает, если не была применена структура (схема) каталогов на LDAP-сервере при настройке
OpenLDAP (либо была применена некорректная схема). Вернитесь на шаг .
Если это не помогло, проверьте, что:
в папке C:\Program Files\OpenLDAP\schema есть файл security.schema;
в файле конфигурации C:\ProgramData\OpenLDAP\openldap\slapd.conf есть строчка:
include
./schema/security.schema
Представленные учетные данные неверны
В этом случае следует проверить каталог администратора, указанный в мастере создания новой
конфигурации Alpha.Security, запускаемом при подключении напрямую к LDAP-серверу из
SecurityConfigurator (стр. 74).
124
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 104 ===
10. РЕШЕНИЕ РАСПРОСТРАНЕННЫХ ПРОБЛЕМ
Если не меняли значение по умолчанию, то в строке Администратор LDAP должно быть указано:
«cn=Manager,dc=maxcrc,dc=com» – если OpenLDAP установлен на Windows;
«cn=admin, dc=maxcrc,dc=com» – если OpenLDAP установлен на Linux.
Объект не существует
Такая ошибка возникает, если была изменена или некорректно удалена база OpenLDAP. Проверьте, что в
папке C:\Program Files\OpenLDAP\data находятся файлы data.mdb и lock.mdb – это и есть база. Если файлы
находятся в папке, а ошибка все равно возникает, то необходимо удалить и повторно установить OpenLDAP.
Обратите внимание, что это приведет к потере созданных ранее конфигураций! Поэтому попробуйте сначала
найти и восстановить файлы data.mdb и lock.mdb, например, в корзине – возможно, они были удалены или
перемещены по ошибке.
ОБРАТИТЕ ВНИМАНИЕ
После удаления OpenLDAP папка C:\Program Files\OpenLDAP остается. Если база была
"сломана", то эту папку нужно удалить, иначе после повторной установки OpenLDAP будет
соединяться со старой, "сломанной" базой.
Другие проблемы
В ОС Windows служба OpenLDAP не запускается
Следует проверить наличие конфигурационного файла slapd.conf в папке
C:\ProgramData\OpenLDAP\openldap. Если файл отсутствует, то нужно скопировать туда его резервную
копию из C:\Program Files\OpenLDAP.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
125

=== Page 105 ===
10. РЕШЕНИЕ РАСПРОСТРАНЕННЫХ ПРОБЛЕМ
В ОС Linux не происходит автоматический выход пользователя из системы,
если длительность сессии или время бездействия истекло
Следует проверить, запущен ли сервис alpha.security.useractivity.service. Чтобы посмотреть список
запущенных сервисов, используйте команду ps aux. Для удобства поиска отфильтруйте результаты с
помощью команды grep:
ps aux | grep alpha.security
Если в списке нет нужного сервиса, необходимо выполнить запуск сервиса
alpha.security.useractivity.service вручную.
Для пользователей DEB-систем: убедитесь также, что выполнен импорт настроек модулей мониторинга (стр.
20).
В ОС Linux необходимо изменить настройки разнонаправленного
резервирования OpenLDAP
Чтобы изменить настройки разнонаправленного резервирования в ОС Linux, нельзя просто заново создать и
применить файл openldap-enable-syncrepl-multiprovider-server.ldif. Cначала придется удалить
прежние настройки, а затем применить новые.
Чтобы удалить прежние настройки, выполните следующие действия:
1. Выгрузите текущую конфигурацию с помощью команды:
sudo slapcat -b cn=config -l ldap-config.ldif
126
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 106 ===
10. РЕШЕНИЕ РАСПРОСТРАНЕННЫХ ПРОБЛЕМ
2. В любом текстовом редакторе измените полученный файл ldap-config.ldif. Например, можно
использовать редактор nano:
sudo nano ldap-config.ldif
Числа, пути и названия могут отличаться от приведенных в примере ниже.
2.1. Удалите запись olcServerID:
olcServerID: 1
entryCSN: 20230417093406.763770Z#000000#000#000000
modifiersName: gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth
modifyTimestamp: 20230417093406Z
2.2. Удалите блок, содержащий модуль syncprov.la:
dn: cn=module{1},cn=config
objectClass: olcModuleList
cn: module{1}
olcModulePath: /usr/lib/ldap
olcModuleLoad: {0}syncprov.la
structuralObjectClass: olcModuleList
entryUUID: be4047c6-714e-103d-91db-cbf1dc15f9bc
creatorsName: gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth
createTimestamp: 20230417093406Z
entryCSN: 20230417093406.762126Z#000000#000#000000
modifiersName: gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth
modifyTimestamp: 20230417093406Z
2.3. Удалите блок, содержащий olcSyncrepl и olcMirrorMode:
olcSyncrepl: {0}rid=001 provider=ldap://1.2.3.4:389 bindmethod=simple
binddn="cn=admin,dc=maxcrc,dc=com" credentials="secret" searchbase="dc=max
crc,dc=com" scope=sub schemachecking=on type=refreshAndPersist retry="30 5
300 3" interval=00:00:05:00
olcSyncrepl: {1}rid=002 provider=ldap://1.2.3.4:389 bindmethod=simple
binddn="cn=admin,dc=maxcrc,dc=com" credentials="secret" searchbase="dc=max
crc,dc=com" scope=sub schemachecking=on type=refreshAndPersist retry="30 5
300 3" interval=00:00:05:00
olcMirrorMode: TRUE
entryCSN: 20230417093406.764528Z#000000#001#000000
modifiersName: gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth
modifyTimestamp: 20230417093406Z
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
127

=== Page 107 ===
10. РЕШЕНИЕ РАСПРОСТРАНЕННЫХ ПРОБЛЕМ
2.4. Удалите блоки, содержащие olcOverlay syncprov:
dn: olcOverlay={0}syncprov,olcDatabase={1}mdb,cn=config
objectClass: olcOverlayConfig
objectClass: olcSyncProvConfig
olcOverlay: {0}syncprov
olcSpSessionlog: 100
structuralObjectClass: olcSyncProvConfig
entryUUID: be407890-714e-103d-91dc-cbf1dc15f9bc
creatorsName: gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth
createTimestamp: 20230417093406Z
entryCSN: 20230417093406.763396Z#000000#000#000000
modifiersName: gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth
modifyTimestamp: 20230417093406Z
dn: olcOverlay={1}syncprov,olcDatabase={1}mdb,cn=config
objectClass: olcOverlayConfig
objectClass: olcSyncProvConfig
olcOverlay: {1}syncprov
structuralObjectClass: olcSyncProvConfig
entryUUID: be414d38-714e-103d-91dd-cbf1dc15f9bc
creatorsName: gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth
createTimestamp: 20230417093406Z
entryCSN: 20230417093406.768839Z#000000#001#000000
modifiersName: gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth
modifyTimestamp: 20230417093406Z
3. Остановите сервис OpenLDAP, а затем убедитесь, что он остановлен:
sudo service slapd stop
sudo systemctl status slapd
4. Очистите папку от прежней конфигурации:
sudo rm -rf /etc/ldap/slapd.d/*
5. Инициализируйте очищенный от прежних настроек файл ldap-config.ldif в slapd.d:
sudo slapadd -b cn=config -l ldap-config.ldif -F /etc/ldap/slapd.d/
6. Поправьте права доступа к папке slapd.d:
sudo chown -R openldap:openldap /etc/ldap/slapd.d/
7. Запустите сервис OpenLDAP, а затем убедитесь, что он запущен:
sudo systemctl start slapd
sudo systemctl status slapd
Прежние настройки разнонаправленного резервирования удалены. Теперь файл openldap-enable-syncrepl-
multiprovider-server.ldif можно создать и применить заново, как описано в разделах, описывающих
настройку разнонаправленного резервирования.
128
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 108 ===
10. РЕШЕНИЕ РАСПРОСТРАНЕННЫХ ПРОБЛЕМ
В ОС Linux не работает временная блокировка пользователя при превышении
количества неудачных попыток входа
Для пользователей DEB-систем: убедитесь, что выполнен импорт настроек модулей мониторинга (стр. 20).
Для пользователей РЕД ОС иногда возникает следующая проблема: после превышения разрешённого
количества неудачных попыток входа пользователь блокируется навсегда, а не на заданный в праве Таймаут
при превышении количества попыток входа, мин (AttempsTimeOut) период времени. Для решения этой
проблемы может понадобиться выполнение инструкции по настройке монитора LDAP. Инструкция приведена
ниже в текущем подразделе.
Чтобы понять, нужно ли выполнять настройку монитора LDAP, перейдите в каталог
/etc/openldap/slapd.d/cn=config. Откройте файл olcDatabase={x}monitor.ldif (на месте x может быть
любая цифра, которую следует запомнить, а название файла может выглядеть как olcDatabase=
{x}Monitor.ldif). Найдите атрибут olcAccess в этом файле. Если его значение отличается от приведенного
ниже, то необходимо будет выполнить настройку монитора LDAP.
olcAccess: {0} to dn.subtree="cn=monitor"
by dn.exact="cn=admin,dc=maxcrc,dc=com"
write by users write by * none
Чтобы настроить монитор LDAP, сделайте следующее:
1. Создайте файл с расширением *.ldif (например, configure.ldif). Добавьте в него указанное
содержимое:
dn: olcDatabase={x}monitor,cn=config
changetype: modify
replace: olcAccess
olcAccess: {0} to dn.subtree="cn=monitor"
by dn.exact="cn=admin,dc=maxcrc,dc=com"
write by users
write by * none
В первой строке на месте x должна быть указана цифра, которая указана в названии файла
/etc/openldap/slapd.d/cn=config/olcDatabase={x}monitor.ldif.
2. Примените созданный файл-схему с помощью команды:
ldapmodify -Y EXTERNAL -H ldapi:/// -f configure.ldif
3. Перезапустите сервис slapd командой:
systemctl restart slapd
4. Откройте файл /etc/openldap/slapd.d/cn=config/olcDatabase={x}monitor.ldif и убедитесь, что
атрибут olcAccess принял правильное (указанное перед инструкцией) значение.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
129

=== Page 109 ===
10. РЕШЕНИЕ РАСПРОСТРАНЕННЫХ ПРОБЛЕМ
5. В терминале выполните команду:
ldapsearch -Y EXTERNAL -H ldapi:/// -b "cn=schema,cn=config" alpha
В полученном ответе команды найдите запись:
dn: cn={x}alpha,cn=schema,cn=config
На месте x может быть любое число. Его необходимо запомнить.
6. Перейдите к каталогу /opt/Automiq/Alpha.Security. Редактируйте расположенные здесь файлы
addOlcAttrType.ldif и editOlcObjectClass.ldif, заменив x в строке dn: cn={x}alpha,cn=schema,cn=config
на число, запомненное на предыдущем шаге.
7. В терминале выполните команду:
chmod +x ./addLockTime.sh
Затем запустите скрипт addLockTime.sh с помощью команды:
./addLockTime.sh
130
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 110 ===
11. ПРИЛОЖЕНИЯ
11. Приложения
Приложение A: Пример конфигурационного файла Агент
Alpha.Security
Приведенный пример конфигурации Агент Alpha.Security описан так, что:
точка доступа Net-агента установлена на локальной рабочей станции;
LDAP-сервер установлен на локальной рабочей станции;
администратором является Manager, как при умолчании;
пользователем по умолчанию является Guest;
трансляция аудита сообщений включена:
описан сервер-потребитель сообщений, установленный на локальной рабочей станции;
категории важности указаны как при умолчании;
трансляция сообщений выполняется в сигналы Alpha.Server;
контроль целостности включен;
заблокировано сочетание клавиш «ctrl+alt+del» и «ctrl+shift+esc», как при умолчании;
настроено подключение к внешнему источнику учетных данных.
<Alpha.Security.Agent>
<EntryPointNetAgent Address="127.0.0.1" Port="1010"/>
<LdapHosts>
<LDAPServer Address="127.0.0.1" Port="389"/>
</LdapHosts>
<LdapUser value="cn=Manager,dc=maxcrc,dc=com"/>
<LdapPassword
value="...Wq7cRi9SdqyWWWYzUuxoio7F7dLaIEDeRwlee1PlcBlpLfL17KnI..."/>
<LdapSecure value="False"/>
<SecurityDn value="ou=AlphaSecurity,dc=maxcrc,dc=com"/>
<DefaultUser value="Guest"/>
<DefaultUserPassword value="VuZyuLC...JFchMHvKXNeztHoFpe24v2Wl9viv"/>
<GuestDisplayName value=""/>
<mesPrefix value=""/>
<AuditLogConsumers TraceAudit="1">
<OpcDaLogConsumer>
<Server Host="127.0.0.1" Type="OPC" ProgId="AP.OPCDAServer"
TCPServerPort="4388" HostTcpReserve="" MasterPasswordCipher="">
<SeverityMap>
<Severity Category="Critical" Value="800"/>
<Severity Category="Important" Value="200"/>
<Severity Category="Info" Value="100"/>
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
131

=== Page 111 ===
11. ПРИЛОЖЕНИЯ
<Severity Category="Debug" Value="0"/>
</SeverityMap>
<SignalMap>
<Signal Name="DynEvents.NormalDynSignal" Mode="DynamicEvent"
Type="Normal"/>
<Signal Name="DynEvents.AdminDynSignal" Mode="DynamicEvent" Type="Admin"/>
<Signal Name="DynEvents.UserNameDynSignal" Mode="DynamicEvent"
Type="UserName"/>
<Signal Name="DynEvents.DisplayNameDynSignal" Mode="DynamicEvent"
Type="DisplayName"/>
<Signal Name="DynEvents.GroupNameDynSignal" Mode="DynamicEvent"
Type="GroupName"/>
<Signal Name="DynEvents.WorkstationNameDynSignal" Mode="DynamicEvent"
Type="WorkstationName"/>
<Signal Name="DynEvents.NormalMessage" Mode="Value" Type="Normal"/>
<Signal Name="DynEvents.AdminMessage" Mode="Value" Type="Admin"/>
<Signal Name="DynEvents.UserNameMessage" Mode="Value" Type="UserName"/>
<Signal Name="DynEvents.DisplayNameMessage" Mode="Value"
Type="DisplayName"/>
<Signal Name="DynEvents.GroupNameMessage" Mode="Value" Type="GroupName"/>
<Signal Name="DynEvents.WorkstationNameMessage" Mode="Value"
Type="WorkstationName"/>
</SignalMap>
</Server>
</OpcDaLogConsumer>
</AuditLogConsumers>
<Options LoggerLevel="2" ICMode="1"
kbDriverString="0x1D+0x38+0x53;0x1D+0x2A+0x01;" UseRightsCacheStorage="0" />
<ExternalAuthenticationSource>
<Source SourceID = "Source1" Address="111.111.1.1" Port="389" Secure = "False"
>
<MappedAttributes login = "uid" fistname = "givenName" midname = "initials"
lastname = "sn" description = "company"
displayname = "displayName" email = "mail" position = "title" objectSid =
"ipaNTSecurityIdentifier" objectGUID = "ipaUniqueID"/>
<LoginTemplate value = "uid={login},cn=users,cn=accounts,{domainDN}" />
</Source>
</ExternalAuthenticationSource>
</Alpha.Security.Agent>
132
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 112 ===
11. ПРИЛОЖЕНИЯ
Приложение B: SCAN-коды клавиш
Название клавиши
Код
Esc
0x01
Win левый
0x5B
Win правый
0x5C
Caps Lock
0x3A
Tab
0x0F
Shift левый
0x2A
Shift правый
0x36
Ctrl
0x1D
Alt
0x38
F1
0x3B
F2
0x3C
F3
0x3D
F4
0x3E
F5
0x3F
F6
0x40
F7
0x41
F8
0x42
F9
0x43
F10
0x44
F11
0x57
F12
0x58
←Backspace
0x0E
Enter
0x1C
↑
0x48
↓
0x50
←
0x4B
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
133

=== Page 113 ===
11. ПРИЛОЖЕНИЯ
Название клавиши
Код
→
0x4D
Пробел
0x39
PrtSc
0x54
Scroll Lock
0x46
Pause/Break
0x45
Insert
0x52
Home
0x47
Page Up
0x49
Delete
0x53
End
0x4F
Page Down
0x51
Num Lock
0x45
] }
0x1B
[ {
0x1A
= +
0x0D
; :
0x27
/ ?
0x35
. >
0x34
- _
0x0C
' "
0x28
< ,
0x33
|
0x2B
A
0x1E
B
0x30
C
0x2E
D
0x20
E
0x12
134
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 114 ===
11. ПРИЛОЖЕНИЯ
Название клавиши
Код
F
0x21
G
0x22
H
0x23
I
0x17
J
0x24
K
0x25
L
0x26
M
0x32
N
0x31
O
0x18
P
0x19
Q
0x10
R
0x13
S
0x1F
T
0x14
U
0x16
V
0x2F
W
0x11
X
0x2D
Y
0x15
Z
0x2C
0
0xB
1
0x2
2
0x3
3
0x4
4
0x5
5
0x6
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
135

=== Page 115 ===
11. ПРИЛОЖЕНИЯ
Название клавиши
Код
6
0x7
7
0x8
8
0x9
9
0xA
136
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 116 ===
11. ПРИЛОЖЕНИЯ
Приложение C: Параметры запуска SecurityConfigurator
Параметр
Описание и пример
WindowsFixed
Для главного окна приложения и его дочерних окон заблокирована возможность
менять положение или размер.
alpha.security.configurator.exe WindowsFixed
FileSystemSafeMode
Управление режимом ограничения доступа к файловой системе. Блокирует
возможность вызова окна справки.
alpha.security.configurator.exe FileSystemSafeMode
Height, Width
Размер главного окна приложения при запуске:
Height – высота окна;
Width – ширина окна.
ОБРАТИТЕ ВНИМАНИЕ
Если указан один параметр, второй параметр должен быть указан
обязательно.
alpha.security.configurator.exe Width 800 Height 600
Top, Left
Положение главного окна приложения при запуске:
Top – расстояние от верхней границы экрана до окна;
Left – расстояние от левой границы экрана до окна.
ОБРАТИТЕ ВНИМАНИЕ
Если указан один параметр, второй параметр должен быть указан
обязательно.
alpha.security.configurator.exe Top 200 Left 100
SetScreen
Номер монитора, на котором требуется отобразить главное окно приложения при
запуске. Номера мониторов заданы в настройках ОС.
Окно конфигуратора откроется на указанном мониторе в тех же координатах, в
которых было закрыто в последний раз.
alpha.security.configurator.exe SetScreen 2
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
137

=== Page 117 ===
11. ПРИЛОЖЕНИЯ
Параметр
Описание и пример
AlwaysOnTop
Главное окно приложения будет всегда отображаться поверх других окон.
ПРИМЕЧАНИЕ
Окно может быть перекрыто окном другого приложения Альфа
платформы (например Alpha.HMI.Alarms), если оно тоже запущено с
параметром AlwaysOnTop.
alpha.security.configurator.exe AlwaysOnTop
138
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 118 ===
11. ПРИЛОЖЕНИЯ
Приложение D: Права системного приложения
Alpha.Security
Право
Краткое
описание
Описание
ActivityLimitedToOneWorkstationOnly
Пользователь
может быть
активен только на
одном ARM
Используется, чтобы пользователь мог
быть активен не более чем на одном АРМ.
Используйте вместе с правом
ForceStopOldUserSessionOnNewLogin для
принудительного завершения активной
сессии пользователя, если он выполняет
вход на новом АРМ.
Этим правом автоматически наделяется
администратор текущего каталога LDAP.
При создании новой учетной записи
администратора следует назначить ему это
право со значением Запретить.
AttempsTimeOut
Таймаут
блокировки при
превышении
количества
неуспешных
попыток входа,
мин
Длительность блокировки пользователя при
превышении количества неудачных
попыток, указанных в MaxAttempsCount.
Эффективным значением права является
максимальное значение.
ConfigurationAccess
Редактирование
конфигурации
Предоставляет доступ к редактированию
конфигурации Alpha.Security.
Этим правом автоматически наделяется
администратор текущего каталога LDAP.
При создании новой учетной записи
администратора следует назначить ему это
право со значением Разрешить.
EditSettings
Изменение
настроек
Предоставляет доступ к настройкам
SecurityConfigurator.
Этим правом автоматически наделяется
администратор текущего каталога LDAP.
При создании новой учетной записи
администратора следует назначить ему это
право со значением Разрешить.
ForceStopOldUserSessionOnNewLogin
Завершать
сессию на
активном
ARM при входе
пользователя на
другом ARM
Используется для принудительного
завершения активной сессии пользователя,
если он выполняет вход на новом АРМ.
Этим правом автоматически наделяется
администратор текущего каталога LDAP.
При создании новой учетной записи
администратора следует назначить ему это
право со значением Разрешить.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
139

=== Page 119 ===
11. ПРИЛОЖЕНИЯ
Право
Краткое
описание
Описание
InteractiveLogon
Интерактивный
вход
Используется для установки разрешения
или запрета на вход.
Этим правом автоматически наделяется
администратор текущего каталога LDAP.
При создании новой учетной записи
администратора следует назначить ему это
право со значением Разрешить.
Вместе с тем позволяет исключить учетную
запись из списка пользователей,
предоставляемого по запросу. Например:
из выпадающего списка
пользователей в окне входа в
конфигураторе;
из списка, запрашиваемого
компонентом Список пользователей
расширения Alpha.HMI.Security.
LowerCount
Количество в
пароле символов
в нижнем регистре
Устанавливает минимально допустимое
количество символов в нижнем регистре в
пароле.
Эффективным значением права является
максимальное значение.
MaxAttempsCount
Количество
попыток входа,
шт
Устанавливает количество неудачных
попыток входа для пользователя. Если
пользователь не войдет за указанное
количество попыток, то блокируется на
время, указанное в AttempsTimeOut.
При вводе неправильного пароля Агент
Alpha.Security сообщает о количестве
оставшихся попыток входа до временной
блокировки.
Эффективным значением права является
минимальное значение.
MaxIdleTime
Максимальное
время
бездействия, мин
Устанавливает время бездействия
пользователя. Таймер сбрасывается при
каждом взаимодействии пользователя с
АРМ – щелчком или движением мыши,
вводом текста с клавиатуры и т.д. Если же
за указанное время пользователь не
взаимодействует с АРМ, происходит
автоматический выход пользователя из
системы.
Эффективным значением права является
минимальное значение.
140
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 120 ===
11. ПРИЛОЖЕНИЯ
Право
Краткое
описание
Описание
NonDeletableWhileActive
Запрет удаления
активного
пользователя
Устанавливает запрет на удаление учетной
записи, если пользователь активен.
Этим правом автоматически наделяется
администратор текущего каталога LDAP.
При создании новой учетной записи
администратора следует назначить ему это
право со значением Разрешить.
NumbersCount
Количество
цифровых
символов в
пароле
Устанавливает минимально допустимое
количество цифр в пароле.
Эффективным значением права является
максимальное значение.
PasswordAge
Срок действия
пароля, дней
Устанавливает границы срока действия
пароля.
До истечения минимального срока действия
обновить пароль нельзя.
После истечения максимального срока
действия пароля попытки входа со старыми
учетными данными будут отклоняться.
Эффективным значением минимального
срока является максимальное значение.
Эффективным значением максимального
срока является минимальное значение.
PasswordComplexity
Сложность
пароля
Обязательность использования в пароле
следующих видов символов:
цифры;
буквы нижнего регистра;
буквы верхнего регистра;
специальные символы.
Эффективным значением является
сочетание всех указанных символов.
PasswordComposition
Состав пароля
Позволяет ограничить набор доступных
символов для пароля:
только цифры,
только символы нижнего регистра,
только символы верхнего регистра,
только символы,
либо сочетание перечисленных ограничений.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
141

=== Page 121 ===
11. ПРИЛОЖЕНИЯ
Право
Краткое
описание
Описание
PasswordMinLength
Минимальная
длина пароля
Устанавливает минимально допустимое
количество символов в пароле.
Эффективным значением права является
максимальное значение.
PasswordNotContainUserData
Проверка наличия
пользовательских
данных в пароле
Проверяет наличие логина, имени, фамилии
и/или отображаемого имени пользователя в
его пароле. Проверка выполняется без учета
регистра. Эффективным значением права
является Нет (установлено по умолчанию). В
этом случае пароль может содержать
пользовательские данные.
PasswordNotifyForChange
Уведомление о
смене пароля,
дней
Позволяет создать напоминание об
истечении срока действия пароля для
пользователя. За указанное до истечения
пароля время будет отправлено
напоминание о скором истечении срока
действия пароля.
Эффективным значением является
максимальное значение.
PasswordsInHistory
Количество
паролей в истории
Устанавливает количество хранимых в
истории паролей. Обновить пароль на такой
же, как в истории паролей, не получится.
Эффективным значением является
максимальное значение.
SessionDurationLimit
Максимальное
время сессии,
мин
Устанавливает длительность сессии
пользователя. После истечения указанного
времени происходит автоматический выход
пользователя из системы.
Эффективным значением является
минимальное значение.
SpecialCount
Количество
специальных
символов в
пароле
Устанавливает минимально допустимое
количество специальных символов в
пароле.
?
!
@
#
$
%
^
&
№
<
>
_
-
=
+
*
(
)
[
]
{
}
.
,
:
;
~
`
'
"
\
|
/
Специальные символы
Эффективным значением права является
максимальное значение.
142
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 122 ===
11. ПРИЛОЖЕНИЯ
Право
Краткое
описание
Описание
UpperCount
Количество в
пароле символов
в верхнем
регистре
Устанавливает минимально допустимое
количество символов в верхнем регистре в
пароле.
Эффективным значением права является
максимальное значение.
UserSessionHoldTimeout
Время сохранения
сессии
пользователя при
разрыве связи
агента
безопасности с
хранилищем, сек
Устанавливает время сохранения сессии
пользователя при разрыве связи агента
безопасности с LDAP-сервером.
Принимает значения в диапазоне от «0» до
«86400». Если значение не задано или равно
«0», то при разрыве связи сессия не будет
сохранена.
Значение по умолчанию: «60».
Эффективным значением права является
минимальное значение.
ViewConfiguration
Просмотр
конфигурации
Предоставляет доступ к просмотру
конфигурации Alpha.Security без
возможности редактирования.
Этим правом автоматически наделяется
администратор текущего каталога LDAP.
При создании новой учетной записи
администратора следует назначить ему это
право со значением Разрешить.
WinKeysShortcutAccess
Доступ к
сочетаниям
клавиш Windows
Предоставляет доступ к использованию
сочетаний клавиш (так называемых
Hotkeys).
Чтобы использовать сочетания клавиш, их
необходимо настроить. Подробнее об этом в
4. Агент безопасности и его настройка (стр.
64).
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
143

=== Page 123 ===
11. ПРИЛОЖЕНИЯ
Приложение E: Сообщения аудита
В данном приложении приведена таблица с расшифровкой текстов сообщений аудита из файла
alpha.security.agent.json в более удобном для понимания виде. В столбце name приведены
идентификаторы сообщений, в столбце value – шаблоны текстов сообщений о событиях, регистрируемых
подсистемой безопасности. Помните о том, что тексты сообщений можно менять. Подробнее об этом – в
разделе 7. Аудит безопасности (стр. 110).
name
value
AUDIT_ADD_
USER
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: Добавлен пользователь <имя пользователя>.
AUDIT_
DELETE_USER
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: Удален пользователь <имя пользователя>.
AUDIT_
DELETE_
USER_FAILED
Неудачная попытка удалить пользователя <имя пользователя> на указанном АРМ от
имени указанного пользователя: его сессия активна на узле <название АРМ>
AUDIT_
DELETE_
USER_GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: Удален пользователь <имя пользователя> группа
<название группы>.
AUDIT_
DELETE_
USER_GROUP_
FAILED
Неудачная попытка удалить пользователя <имя пользователя> на указанном АРМ от
имени указанного пользователя, состоящем в указанной группе: его сессия активна на
узле <название АРМ>
AUDIT_USER_
LOGIN_ADD
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> задан логин:
<логин пользователя>.
AUDIT_USER_
NAME_ADD
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> задано имя: <имя
пользователя>.
AUDIT_USER_
SURNAME_
ADD
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> задана фамилия:
<фамилия пользователя>.
AUDIT_USER_
THIRD_ADD
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> задано отчество:
<отчество пользователя>.
AUDIT_USER_
POSITION_ADD
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> задана должность:
<должность пользователя>.
AUDIT_USER_
DEPARTMENT_
ADD
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> задано
подразделение: <название подразделения>.
144
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 124 ===
11. ПРИЛОЖЕНИЯ
name
value
AUDIT_USER_
MAIL_ADD
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> задан адрес
почты: <адрес>.
AUDIT_USER_
PHONE_ADD
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> задан телефон:
<номер телефона>.
AUDIT_USER_
DESCRIPTION_
ADD
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> заданы
дополнительные данные: <описание для УЗ пользователя>.
AUDIT_USER_
LOGIN_MODIFY
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> изменен логин:
значение <значение> заменено на <значение>.
AUDIT_USER_
LOGIN_
MODIFY_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> группа <название
группы> изменен логин: значение <значение> заменено на <значение>.
AUDIT_USER_
NAME_MODIFY
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> изменено имя:
значение <значение> заменено на <значение>.
AUDIT_USER_
NAME_
MODIFY_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> группа <название
группы> изменено имя: значение <значение> заменено на <значение>.
AUDIT_USER_
SURNAME_
MODIFY
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> изменена
фамилия: значение <значение> заменено на <значение>.
AUDIT_USER_
SURNAME_
MODIFY_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> группа <название
группы> изменена фамилия: значение <значение> заменено на <значение>.
AUDIT_USER_
POSITION_
MODIFY
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> изменена
должность: значение <значение> заменено на <значение>.
AUDIT_USER_
POSITION_
MODIFY_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> группа <название
группы> изменена должность: значение <значение> заменено на <значение>.
AUDIT_USER_
DEPARTMENT_
MODIFY
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> изменено
подразделение: значение <значение> заменено на <значение>.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
145

=== Page 125 ===
11. ПРИЛОЖЕНИЯ
name
value
AUDIT_USER_
DEPARTMENT_
MODIFY_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> группа <название
группы> изменено подразделение: значение <значение> заменено на <значение>.
AUDIT_USER_
MAIL_MODIFY
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> изменен адрес
почты: значение <значение> заменено на <значение>.
AUDIT_USER_
MAIL_MODIFY_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> группа <название
группы> изменен адрес почты: значение <значение> заменено на <значение>.
AUDIT_USER_
PHONE_
MODIFY
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> изменен телефон:
значение <значение> заменено на <значение>.
AUDIT_USER_
PHONE_
MODIFY_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> группа <название
группы> изменен телефон: значение <значение> заменено на <значение>.
AUDIT_USER_
PASS_MODIFY
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> изменен пароль.
AUDIT_USER_
PASS_
MODIFY_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> группа <название
группы> изменен пароль.
AUDIT_USER_
DESCRIPTION_
MODIFY
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> изменены
допольнительные данные: значение <значение> заменено на <значение>.
AUDIT_USER_
DESCRIPTION_
MODIFY_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> группа <название
группы> изменены допольнительные данные: значение <значение> заменено на
<значение>.
AUDIT_USER_
DISP_MODIFY
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> изменено
отображаемое имя: значение <значение> заменено на <значение>.
AUDIT_USER_
DISP_MODIFY_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> группа <название
группы> изменено отображаемое имя: значение <значение> заменено на <значение>.
AUDIT_USER_
THIRD_MODIFY
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> изменено
отчество: значение <значение> заменено на <значение>.
146
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 126 ===
11. ПРИЛОЖЕНИЯ
name
value
AUDIT_USER_
THIRD_
MODIFY_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> группа <название
группы> изменено отчество: значение <значение> заменено на <значение>.
AUDIT_USER_
DISABLED_
MODIFY
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> изменен атрибут
заблокирован: значение <значение> заменено на <значение>.
AUDIT_USER_
DISABLED_
MODIFY_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> группа <название
группы> изменен атрибут заблокирован: значение <значение> заменено на <значение>.
AUDIT_USER_
RIGHT_ADD
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: Пользователю <имя пользователя> назначено право
<название права> (<описание права>) из приложения <название приложения>.
Разрешено: <значение>, запрещено: <значение>.
AUDIT_USER_
RIGHT_ADD_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: Пользователю <имя пользователя> группа <название
группы> назначено право <название права> (<описание права>) из приложения
<название приложения>. Разрешено: <значение>, запрещено: <значение>.
AUDIT_USER_
RIGHT_ADD_
NUMBER
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: Пользователю <имя пользователя> назначено право
<название права> (<описание права>) из приложения <название приложения>. Значение:
<значение>
AUDIT_USER_
RIGHT_ADD_
NUMBER_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: Пользователю <имя пользователя> группа <название
группы> назначено право <название права> (<описание права>) из приложения
<название приложения>. Значение: <значение>
AUDIT_USER_
RIGHT_ADD_
RANGE
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: Пользователю <имя пользователя> назначено право
<название права> (<описание права>) из приложения <название приложения>. Мин.
значение: <значение>, Макс. значение: <значение>
AUDIT_USER_
RIGHT_ADD_
RANGE_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: Пользователю <имя пользователя> группа <название
группы> назначено право <название права> (<описание права>) из приложения
<название приложения>. Мин. значение: <значение>, Макс. значение: <значение>
AUDIT_USER_
RIGHT_DELETE
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> удалено право
<название права> из приложения <название приложения>.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
147

=== Page 127 ===
11. ПРИЛОЖЕНИЯ
name
value
AUDIT_USER_
RIGHT_
DELETE_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> группа <название
группы> удалено право <название права> из приложения <название приложения>.
AUDIT_USER_
RIGHT_
MODIFY_
ALLOWED
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> изменено
разрешенное значение для права <название права> (<описание права>) из приложения
<название приложения>: старое значение - <значение>, значение - <значение>.
AUDIT_USER_
RIGHT_
MODIFY_
ALLOWED_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> группа <название
группы> изменено разрешенное значение для права <название права> (<описание
права>) из приложения <название приложения>: старое значение - <значение>, значение
- <значение>.
AUDIT_USER_
RIGHT_
MODIFY_
DENIED
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> изменено
запрещенное значение для права <название права> (<описание права>) из приложения
<название приложения>: старое значение - <значение>, значение - <значение>.
AUDIT_USER_
RIGHT_
MODIFY_
DENIED_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> группа <название
группы> изменено запрещенное значение для права <название права> (<описание
права>) из приложения <название приложения>: старое значение - <значение>, значение
- <значение>.
AUDIT_USER_
FAILED_
CHANGE_
PASS_OLD
Неудачная попытка сменить пароль пользователя указанного пользователя на
указанном АРМ: неправильный старый пароль.
AUDIT_USER_
FAILED_
CHANGE_
PASS_OLD_
GROUP
Неудачная попытка сменить пароль пользователя указанного пользователя, состоящем
в указанной группе на указанном АРМ: неправильный старый пароль.
AUDIT_USER_
RIGHT_
MODIFY_
SPECIAL_
ALLOWED
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> изменено
значение для права <название права> (<описание права>) из приложения <название
приложения>: Старое значение - <значение> значение - <значение>.
AUDIT_USER_
RIGHT_
MODIFY_
SPECIAL_
ALLOWED_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> группа <название
группы> изменено значение для права <название права> (<описание права>) из
приложения <название приложения>: Старое значение - <значение> значение -
<значение>.
148
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 128 ===
11. ПРИЛОЖЕНИЯ
name
value
AUDIT_USER_
RIGHT_
MODIFY_
SPECIAL_
ALLOWED_
DENIED
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> изменено
значение для права <название права> (<описание права>) из приложения <название
приложения>: Минимальное значение - <значение> (старое - <значение>), максимальное
значение - <значение> (старое - <значение>).
AUDIT_USER_
RIGHT_
MODIFY_
SPECIAL_
ALLOWED_
DENIED_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> группа <название
группы> изменено значение для права <название права> (<описание права>) из
приложения <название приложения>: Минимальное значение - <значение> (старое -
<значение>), максимальное значение - <значение> (старое - <значение>).
AUDIT_USER_
ROLE_ADD
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: Пользователю <имя пользователя> добавлена роль:
<название роли>.
AUDIT_USER_
ROLE_ADD_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: Пользователю <имя пользователя> группа <название
группы> добавлена роль: <название роли>.
AUDIT_USER_
ROLE_DELETE
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> удалена роль:
<название роли>.
AUDIT_USER_
ROLE_
DELETE_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: У пользователя <имя пользователя> группа <название
группы> удалена роль: <название роли>.
AUDIT_USER_
DISABLED
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: Аккаунт пользователя <имя пользователя>
заблокировн.
AUDIT_USER_
DISABLED_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: Аккаунт пользователя <имя пользователя> группа
<название группы> заблокировн.
AUDIT_USER_
ENABLED
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: Аккаунт пользователя <имя пользователя>
разблокирован.
AUDIT_USER_
ENABLED_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе,
изменен список пользователей: Аккаунт пользователя <имя пользователя> группа
<название группы> разблокирован.
AUDIT_ADD_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка групп - Добавлена группа пользователей <название группы>.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
149

=== Page 129 ===
11. ПРИЛОЖЕНИЯ
name
value
AUDIT_
DELETE_
GROUP
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка групп - Удалена группа пользователей <название группы>.
AUDIT_
GROUP_
SYMBOLIC_
ADD
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка групп - У группы пользователей <название группы> задан
идентификатор: <название группы>.
AUDIT_
GROUP_USER_
ADD
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка групп - В группу пользователей <название группы> добавлен
пользователь: <имя пользователя>.
AUDIT_
GROUP_ROLE_
ADD
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка групп - В группу пользователей <название группы> добавлена роль:
<название роли>.
AUDIT_
GROUP_USER_
DELETE
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка групп - Из группы <название группы> удален пользователь <имя
пользователя>.
AUDIT_
GROUP_ROLE_
DELETE
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка групп - Из группы <название группы> удалена роль <название роли>.
AUDIT_
GROUP_
SYMBOLIC_
MODIFY
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка групп - У группы пользователей <название группы> изменен
идентификатор: значение <значение> заменено на <значение>.
AUDIT_
GROUP_
RIGHT_ADD
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка групп - Группе <название группы> назначено право <название права>
(<описание права>) из приложения <название приложения>. Разрешено: <значение>,
запрещено: <значение>.
AUDIT_
GROUP_
RIGHT_ADD_
NUMBER
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка групп - Группе <название группы> назначено право <название права>
(<описание права>) из приложения <название приложения>. Значение: <значение>.
AUDIT_
GROUP_
RIGHT_ADD_
RANGE
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка групп - Группе <название группы> назначено право <название права>
(<описание права>) из приложения <название приложения>. Мин. значение: <значение>,
макс. значение: <значение>.
AUDIT_
GROUP_
RIGHT_
MODIFY_
ALLOWED
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка групп - У группы <название группы> изменено разрешенное значение
для права <название права> (<описание права>) из приложения <название приложения>:
старое значение - <значение>, значение - <значение>.
150
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 130 ===
11. ПРИЛОЖЕНИЯ
name
value
AUDIT_
GROUP_
RIGHT_
MODIFY_
DENIED
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка групп - У группы <название группы> изменено запрещенное значение
для права <название права> (<описание права>) из приложения <название приложения>:
старое значение - <значение>, значение - <значение>.
AUDIT_
GROUP_
RIGHT_DELETE
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка групп - У группы <название группы> удалено право <название права>
из приложения <название приложения>.
AUDIT_
GROUP_
DISPLAY_
MODIFY
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка групп - У группы пользователей <название группы> изменено
отображаемое имя: значение <значение> заменено на <значение>.
AUDIT_
GROUP_
DISABLED_
MODIFY
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка групп - У группы пользователей <название группы> изменен атрибут
заблокирован: значение <значение> заменено на <значение>.
AUDIT_
GROUP_
RIGHT_
MODIFY_
SPECIAL_
ALLOWED
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка групп - У группы пользователей <имя пользователя> изменено
значение для права <название права> (<описание права>) из приложения <название
приложения>: Старое значение - <значение> значение - <значение>.
AUDIT_
GROUP_
RIGHT_
MODIFY_
SPECIAL_
ALLOWED_
DENIED
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка групп - У группы пользователей <имя пользователя> изменено
значение для права <название права> (<описание права>) из приложения <название
приложения>: Минимальное значение - <значение> (старое - <значение>), максимальное
значение - <значение> (старое - <значение>).
AUDIT_ADD_
TOKEN
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка прав - Добавлен токен безопасности <название права> приложения
<название приложения>.
AUDIT_
DELETE_
TOKEN
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка прав - Удален токен безопасности <название права> приложения
<название приложения>.
AUDIT_TOKEN_
DESCRIPTION_
ADD
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка прав - У токена безопасности <название права> приложения
<название приложения> задано описание: <описание права>.
AUDIT_TOKEN_
DESCRIPTION_
MODIFY
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка прав - У токена безопасности <название права> приложения
<название приложения> изменено описание: значение <значение> заменено на
<значение>.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
151

=== Page 131 ===
11. ПРИЛОЖЕНИЯ
name
value
AUDIT_ADD_
APPLICATION
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка приложений - Добавлено приложение <название приложения>.
AUDIT_
DELETE_
APPLICATION
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка приложений - Удалено приложение <название приложения>.
AUDIT_ROLE_
ADD
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка ролей в приложении <название приложения> - Приложению <название
приложения> добавлена роль <название роли>.
AUDIT_ROLE_
DELETE
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка ролей в приложении <название приложения> - У приложения
<название приложения> удалена роль <название роли>.
AUDIT_APP_
NAME_MODIFY
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка ролей в приложении <название приложения> - У приложения
<название приложения> измненено имя: значение <значение> заменено на <значение>.
AUDIT_ROLE_
RIGHT_ADD
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка ролей в приложении <название приложения> - Роли <название роли>
назначено право <название права> (<описание права>) из приложения <название
приложения>. Разрешено: <значение>, запрещено: <значение>.
AUDIT_ROLE_
RIGHT_ADD_
NUMBER
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка ролей в приложении <название приложения> - Роли <название роли>
назначено право <название права> (<описание права>) из приложения <название
приложения>. Значение: <значение>.
AUDIT_ROLE_
RIGHT_ADD_
RANGE
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка ролей в приложении <название приложения> - Роли <название роли>
назначено право <название права> (<описание права>) из приложения <название
приложения>. Мин. значение: <значение>, макс. значение: <значение>.
AUDIT_ROLE_
RIGHT_
MODIFY_
ALLOWED
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка ролей в приложении <название приложения> - У роли <название роли>
изменено разрешенное значение для права <название права> (<описание права>) из
приложения <название приложения>: старое значение - <значение>, значение -
<значение>.
AUDIT_ROLE_
RIGHT_
MODIFY_
DENIED
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка ролей в приложении <название приложения> - У роли <название роли>
изменено запрещенное значение для права <название права> (<описание права>) из
приложения <название приложения>: старое значение - <значение>, значение -
<значение>.
AUDIT_ROLE_
RIGHT_DELETE
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка ролей в приложении <название приложения> - У роли <название роли>
удалено право <название права> из приложения <название приложения>.
152
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 132 ===
11. ПРИЛОЖЕНИЯ
name
value
AUDIT_ROLE_
NAME_MODIFY
На указанном АРМ от имени указанного пользователя, состоящем в указанной группе:
Настройка списка ролей в приложении <название приложения> - У роли <название роли>
в приложении <название приложения> изменено имя: значение <значение> заменено на
<значение>.
AUDIT_USER_
LOGON
Пользователь <логин пользователя> вошел в систему на указанном АРМ.
AUDIT_USER_
LOGON_
GROUP
Пользователь <логин пользователя> группа <название группы> вошел в систему на
указанном АРМ.
AUDIT_USER_
LOGOFF
Пользователь указанного пользователя вышел из системы на указанном АРМ.
AUDIT_USER_
LOGOFF_
GROUP
Пользователь указанного пользователя, состоящем в указанной группе вышел из
системы на указанном АРМ.
AUDIT_USER_
LOGOFF_
FORCE
Завершен сеанс пользователя <логин пользователя> по запросу учетной записи <логин
пользователя> [Компьютер указанном АРМ].
AUDIT_USER_
LOGOFF_
GROUP_
FORCE
Завершен сеанс пользователя <логин пользователя>, состоящем в указанной группе по
запросу учетной записи <логин пользователя> [Компьютер указанном АРМ].
AUDIT_USER_
LOGOFF_
FORCE_
GROUP
Завершен сеанс пользователя <логин пользователя> по запросу учетной записи <логин
пользователя> группа <название группы> [Компьютер указанном АРМ].
AUDIT_USER_
LOGOFF_
GROUP_
FORCE_
GROUP
Завершен сеанс пользователя <логин пользователя>, состоящем в указанной группе по
запросу учетной записи <логин пользователя> группа <название группы> [Компьютер
указанном АРМ].
AUDIT_USER_
LOGOFF_
INACTIVE
Пользователь указанного пользователя вышел из системы на указанном АРМ, т.к.
превышено максимальное время бездействия.
AUDIT_USER_
LOGOFF_
GROUP_
INACTIVE
Пользователь указанного пользователя, состоящем в указанной группе вышел из
системы на указанном АРМ, т.к. превышено максимальное время бездействия.
AUDIT_USER_
LOGOFF_
TIMEOUT
Произведён выход пользователя указанного пользователя из системы на указанном
АРМ, т.к. закончилось максимально допустимое время сессии.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
153

=== Page 133 ===
11. ПРИЛОЖЕНИЯ
name
value
AUDIT_USER_
LOGOFF_
TIMEOUT_
GROUP
Произведён выход пользователя указанного пользователя, состоящем в указанной
группе из системы на указанном АРМ, т.к. закончилось максимально допустимое время
сессии.
AUDIT_USER_
FAILED_LOGIN
Неудачная попытка входа пользователя <логин пользователя> в систему на указанном
АРМ.
AUDIT_USER_
FAILED_
CHANGE_
PASS_
WRONG_OS
Неудачная попытка сменить пароль пользователя <имя пользователя> на указанном
АРМ: Учетная запись принадлежит ActiveDirectory или ОС Windows.
AUDIT_USER_
FAILED_
CHANGE_
PASS_MIN
Неудачная попытка сменить пароль пользователя <имя пользователя> на указанном
АРМ: минимальный срок не истёк.
AUDIT_USER_
FAILED_
CHANGE_
PASS_MIN_
GROUP
Неудачная попытка сменить пароль пользователя <имя пользователя> группа
<название группы> на указанном АРМ: минимальный срок не истёк.
AUDIT_USER_
FAILED_
CHANGE_
PASS_INVALID
Неудачная попытка сменить пароль пользователя <имя пользователя> на указанном
АРМ: пароль не удовлетворяет требованиям.
AUDIT_USER_
FAILED_
CHANGE_
PASS_
INVALID_
GROUP
Неудачная попытка сменить пароль пользователя <имя пользователя> группа
<название группы> на указанном АРМ: пароль не удовлетворяет требованиям.
AUDIT_USER_
SUCCESS_
CHANGE_PASS
На указанном АРМ у пользователя <имя пользователя> успешно изменен пароль.
AUDIT_USER_
SUCCESS_
CHANGE_
PASS_GROUP
На указанном АРМ у пользователя <имя пользователя> группа <название группы>
успешно изменен пароль.
AUDIT_USER_
FAILED_
LOGIN_WITH_
CHANGE
Неудачная попытка входа со сменой пароля для <логин пользователя> на указанном
АРМ : неправильные данные входа.
154
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 134 ===
11. ПРИЛОЖЕНИЯ
name
value
AUDIT_
DEFAULT_
CHANGE_PASS
На указанном АРМ произошла попытка сменить пароль пользователю по умолчанию.
AUDIT_OS_
PASS_CHANGE
На указанном АРМ произошла попытка сменить пароль учетной записи, принадлежащей
Active Directory или ОС Windows.
AUDIT_USER_
DISABLED_
TEMP
Контроль доступа. На указанном АРМ Аккаунт пользователя <логин пользователя>
временно заблокирован. Время до разблокировки <значение> минут(ы).
AUDIT_IC_
REQUEST_
OPERATION
Пользователь <логин пользователя> (группа: <название группы>; сервер: <название
сервера>) запросил операцию <название операции> на <имя компьютера>.
AUDIT_IC_
REQUEST_
ETALON
Пользователь <логин пользователя> (группа: <название группы>; сервер: <название
сервера>) запросил операцию 'Сгенерировать эталон' на <имя компьютера>.
AUDIT_IC_
REQUEST_
CHECK
Пользователь <логин пользователя> (группа: <название группы>; сервер: <название
сервера>) запросил операцию 'Выполнить контроль целостности файлов' на <имя
компьютера>.
AUDIT_IC_
REQUEST_
RESULT
Пользователь <логин пользователя> (группа: <название группы>; сервер: <название
сервера>) запросил операцию 'Получить результаты контроля целостности' на <имя
компьютера>.
AUDIT_IC_
START_
CONTROL
На указанном АРМ под контроль взято <количество> директорий, <количество>
файлов.
AUDIT_IC_
CURRENT_
CONTROL
На указанном АРМ проверяем <количество> директорий, <количество> файлов. Размер
файлов <значение> байт.
AUDIT_IC_
CFG_NOT_
FOUND
На указанном АРМ не найден файл конфигурации Контроля Целостности <имя файла>.
Контроль Целостности не выполняется.
AUDIT_IC_
CFG_
LISTERROR
На указанном АРМ обнаружены ошибки в списке <ICList> конфигурации Контроля
целостности <имя файла>.
AUDIT_IC_
WRONG_
FORMAT
На указанном АРМ некорректное форматирование файла <имя файла>. Контроль
Целостности не выполняется.
AUDIT_IC_
ETALON_NOT_
FOUND
На указанном АРМ не найден эталонный файл контроля целостности <имя файла>.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
155

=== Page 135 ===
11. ПРИЛОЖЕНИЯ
name
value
AUDIT_IC_
ETALON_DIFF_
CONFIG
На указанном АРМ список <ICList> в конфигурации IC не соответствует Эталону.
Контроль выполняется на основании эталона. Рекомендуется привести в соответствие
Эталон и <ICList> или перегенерировать Эталон.
AUDIT_IC_
ETALON_OK_
CONFIG
На указанном АРМ список <ICList> в конфигурации IC соответствует Эталону.
AUDIT_IC_
STATUS
На указанном АРМ контроль целостности: Проверено файлов: '<количество>'.
Обнаружено нарушений <количество>.
AUDIT_IC_
CREATE_
ETHALON
Пользователь <логин пользователя> (группа: <название группы>; сервер: <название
сервера>) создал эталон файлов для контроля целостности на указанном АРМ.
Объектов в эталоне <количество>. Подтверждено <количество> нарушений 'Нет
доступа для чтения'.
AUDIT_IC_
AUTO_CHECK
На указанном АРМ запущена автоматическая проверка целостности файлов.
AUDIT_IC_
MANUAL_
CHECK
Пользователь <имя пользователя> на указанном АРМ запустил проверку целостности
файлов.
AUDIT_IC_
MANUAL_
CHECK_
GROUP
Пользователь <имя пользователя> из группы пользователей <название группы> на
указанном АРМ запустил проверку целостности файлов.
AUDIT_IC_
ALERT
Нарушена целостность файла <имя файла> на указанном АРМ.
AUDIT_IC_
FILE_NOT_
EXIST
Контролируемый объект <имя файла> не может быть прочитан на указанном АРМ.
AUDIT_IC_
WRONG_LINK
Символическая ссылка <имя файла> на несуществующий объект <имя объекта> на
указанном АРМ.
AUDIT_IC_
DATE_
CHANGED
Изменилась дата модификации объекта <имя файла> <дата>.
AUDIT_IC_
CHECK_DIR_
DATE_OFF
Отключена проверка изменения даты модификации объектов.
AUDIT_IC_
CFG_ERRORS
Операция <название операции> не выполнена из-за ошибок в конфигурации на
указанном АРМ. Исправьте ошибки и повторите операцию.
156
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 136 ===
11. ПРИЛОЖЕНИЯ
name
value
AUDIT_IC_
CFG_ERRORS_
WARN
На указанном АРМ контроль целостности выполняется без ограничений на основании
эталона; генерация эталона невозможна до исправления ошибок.
AUDIT_IC_
CREARE_
ETALON_
CANTREAD
Создание эталона: нет доступа для чтения объекта <имя файла> на указанном АРМ.
AUDIT_IC_
CONTROL_
HIDDEN_
CANTREAD
Контроль файлов: эталоном скрыто нарушение 'Нет доступа для чтения' для объекта
<имя файла> на указанном АРМ.
AUDIT_IC_
NEW_OBJECT_
DETECTED
Обнаружен новый объект <имя файла> на указанном АРМ. Дата создания <дата>
AUDIT_FA_
CFG_NOT_
FOUND
На указанном АРМ не найден файл конфигурации Файлового Аудита <имя файла>.
Файловый Аудит не выполняется.
AUDIT_FA_
WRONG_
FORMAT
На указанном АРМ некорректное форматирование файла <имя файла>. Файловый
Аудит не выполняется.
AUDIT_FA_
EVENT
На указанном АРМ: <текст сообщения>.
AUDIT_USER_
FAILED_
COUNTER_
RESET
Сброшен счетчик неудачных попыток авторизации у пользователя <логин
пользователя> по запросу учетной записи <логин пользователя> [Компьютер указанном
АРМ].
AUDIT_USER_
FAILED_
GROUP_
COUNTER_
RESET
Сброшен счетчик неудачных попыток авторизации у пользователя <логин
пользователя> группа <название группы> по запросу учетной записи <логин
пользователя> [Компьютер указанном АРМ].
AUDIT_USER_
FAILED_
COUNTER_
RESET_GROUP
Сброшен счетчик неудачных попыток авторизации у пользователя <логин
пользователя> по запросу учетной записи <логин пользователя> группа <название
группы> [Компьютер указанном АРМ].
AUDIT_USER_
FAILED_
GROUP_
COUNTER_
RESET_GROUP
Сброшен счетчик неудачных попыток авторизации у пользователя <логин
пользователя> группа <название группы> по запросу учетной записи <логин
пользователя> группа <название группы> [Компьютер указанном АРМ].
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
157

=== Page 137 ===
11. ПРИЛОЖЕНИЯ
name
value
AUDIT_UA_
NOCONNECT
Нет связи с модулем UserActivity на указанном АРМ.
AUDIT_UA_
CONNECTED
Установлена связь с модулем UserActivity на указанном АРМ.
AUDIT_LDAP_
CONNECTED
Установлена связь с LDAP-сервером [<адрес>:<порт>].
AUDIT_LDAP_
NOT_
CONNECTED
Нет связи с LDAP-сервером [<адрес>:<порт>].
AUDIT_LDAP_
NO_SERVERS
LDAP-сервера недоступны.
AUDIT_LDAP_
NOW_ACTIVE
Активный LDAP-сервер [<адрес>:<порт>].
AUDIT_
IMPORT_OK
Выполнен импорт конфигурации LDAP.
AUDIT_
IMPORT_FILE_
CORRUPTED
Ошибка при импорте конфигурации. Файл поврежден.
AUDIT_
IMPORT_
DELETE_
ROOT_FAILED
Ошибка при импорте конфигурации. Не удалось удалить корневой каталог.
AUDIT_
IMPORT_LDAP_
ERR
Ошибка при импорте конфигурации. Не удалось связаться с сервером LDAP.
AUDIT_
IMPORT_
ROOT_NOT_
INIT
Ошибка при импорте конфигурации. Корневой каталог не инициализирован.
AUDIT_
IMPORT_
BRAND_
MISSMATCH
Ошибка при импорте конфигурации. Бренд из конфигурации не совпадает с текущим
брендом сборки.
AUDIT_
IMPORT_
INSUFFICIENT_
ACCESS
Ошибка при импорте конфигурации. У пользователя LdapUser недостаточно прав для
данной операции.
158
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 138 ===
11. ПРИЛОЖЕНИЯ
name
value
AUDIT_
IMPORT_
UNKNOWN_
ERR
Неизвестная ошибка при импорте конфигурации.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
159

=== Page 139 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
История изменений
1.7
1.7.4
Исправления
Устранена причина, по которой при перезапуске службы Alpha.Security.Agent старые процессы не
завершались. Из-за этого после перезапуска службы возникали другие проблемы:
не отключался файловый аудит;
некоторые сигналы Alpha.Server, куда записывались сообщения аудита, не получали
актуальных значений.
Исправлена ошибка, из-за которой пропадало соединение между агентом безопасности и Alpha.Net-
агентом.
При изменении значений прав в сообщениях аудита теперь отображаются как новые, так и старые
значения.
При выполнении контроля целостности файлу, который был перемещен из контролируемой папки, а
затем возвращен в нее, ошибочно присваивался статус удаленного.
В ОС Linux аудит изменений файлов теперь по умолчанию отключен.
В ОС Linux сервисы безопасности теперь запускаются автоматически после обновления или
установки Alpha.Security.
1.7.5
Внутренние изменения. Функциональность подсистемы не изменилась.
1.7.6
Обратите внимание: не рекомендуется использовать предыдущую версию 1.7.5 из-за иногда возникающих
ошибок запуска проектов Alpha.HMI, использующих компоненты безопасности.
Исправления
Исправлена ошибка, из-за которой результаты незамедлительной повторной проверки целостности
файлов отличались от результатов предыдущей проверки.
Устранена причина, по которой заблокированные учетные записи пользователей не
разблокировались по истечении времени блокировки.
160
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 140 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Исправлены ошибки генерирования сообщений аудита:
Ранее при изменении обычного значения числового права ошибочно генерировалось два
сообщения аудита - об изменении разрешенного и запрещенного значений права. Теперь
генерируется одно сообщение об изменении значения права.
При изменении значения права Максимальное время сессии старое значение ошибочно
отображалось в секундах вместо минут.
При изменении значения права Срок действия пароля указывалось некорректное старое
значение права.
При изменении значения права Срок действия пароля для группы из нее удалялись и вновь
добавлялись пользователи.
В некоторых сообщениях отсутствовали пробелы, что затрудняло читаемость.
1.7.7
Исправления
Исправлена ошибка, из-за которой при запросе результата проверки целостности файлов и папок
время последней проверки не обновлялось.
Устранена причина, по которой при переводе пользователя из одной группы в другую удавалось
установить его учетной записи пароль, подходящий парольным политикам прежней группы, но не новой.
1.7.9
Новая возможность
Реализована возможность указывать событиям аудита звук и необходимость квитирования. Для этого
обновлены конфигурационные файлы:
В файле alpha.security.agent.xml для карты важности событий <SeverityMap> звук указывается
в качестве значения нового атрибута Sound.
В файле alpha.security.agent.json для каждого шаблона сообщения звук и необходимость
квитирования указываются в качестве значений параметров sound и ackrequired соответственно.
Улучшение
В файле alpha.security.agent.json обновлен шаблон сообщения аудита AUDIT_IC_CREATE_ETHALON2,
уведомляющего о создании эталона.
Исправления
Исправлена ошибка, из-за которой для пользователя не обновлялось количество паролей в истории
при переводе его из группы с назначенным правом "Количество паролей в истории" в группу без такого
права.
Устранена причина, по которой Агент Alpha.Security не мог подписаться на сигналы для генерации
сообщений аудита после перезагрузки АРМ.
1.7.10
Улучшение
В файл alpha.security.agent.json добавлен новый шаблон сообщения, уведомляющего о добавлении роли
пользователю.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
161

=== Page 141 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Исправления
Устранена причина циклической перезагрузки агента безопасности, возникавшей после удаления у
текущего пользователя прав доступа к папке, целостность которой контролировалась агентом.
Теперь при авторизации пользователя после изменения парольных политик всегда требуется
сменить пароль.
1.7.12
Внутренние изменения. Функциональность подсистемы не изменилась.
1.7.14
Улучшения
Появилась возможность исключать логин пользователя из запрашиваемого списка пользователей.
Так, например, в окне входа в конфигураторе логин такого пользователя не отобразится в выпадающем
списке пользователей.
Теперь при ручном запуске проверки целостности на удаленном компьютере в локальный журнал
приходит только одно сообщение аудита о запуске проверки. Ранее приходило два одинаковых
сообщения – от удаленного и от локального агентов безопасности.
Исправление
Устранена причина, по которой при создании эталона на удаленном компьютере в локальном журнале
отображалось сообщение о создании эталона с неправильным именем пользователя, создавшего эталон.
1.7.17
Улучшение
В файле alpha.security.agent.json расширен перечень регистрируемых событий, для которых могут быть
отправлены сообщения аудита безопасности.
Исправление
Устранена критичная ошибка версии 1.7.16, из-за которой служба Alpha.Security.Agent прекращала работу
при попытке добавить, удалить или изменить право или роль приложения.
1.7.18
Исправления
[ОС AstraLinux, Alpha.HMI.SecurityConfigurator] Устранена причина, по которой после добавления
текущего пользователя в группу с правами на просмотр и редактирование конфигурации было
невозможно произвести вход ни под одним пользователем, состоящим в этой группе.
Устранена причина, по которой агент безопасности не предоставлял сообщение об ошибке, если при
попытке входа пользователем был указан неверный пароль.
1.7.19
Исправление
162
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 142 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Устранена причина, по которой не удавалось сменить пароль пользователя, выполняющего вход, если
ужесточилась парольная политика, а предыдущий пароль менялся менее двух дней назад. Теперь значение
права Минимальный срок действия пароля не учитывается, если пароль требуется обновить из-за
несоответствия новым парольным политикам.
1.7.22
Изменения
Устранены ошибки совместимости Alpha.Security отозванных версий 1.7.20 и 1.7.21 с другими
компонентами Альфа платформы.
Теперь при создании учетной записи администратора ему добавляется право Интерактивный вход
(InteractiveLogon).
Обратите внимание, что при переходе к данной версии рекомендуется всем администраторам, чьи
учетные записи созданы в более ранних версиях, добавить право Интерактивный вход
(InteractiveLogon) со значением «true».
Учтены доработки отозванной версии Alpha.Security 1.7.20:
Новые возможности
Добавлены новые права системного приложения Alpha.Security:
Запрет удаления активного пользователя (NonDeletableWhileActive). Используйте его,
чтобы установить запрет на удаление активного пользователя.
Пользователь может быть активен только на одном ARM
(ActivityLimitedToOneWorkstationOnly). Используйте его, чтобы пользователь мог быть активен
не более чем на одном АРМ.
Завершать сессию на активном ARM при входе пользователя на другом ARM
(ForceStopOldUserSessionOnNewLogin). Если для пользователя установлено ограничение правом
Пользователь может быть активен только на одном ARM
(ActivityLimitedToOneWorkstationOnly), то это право можно использовать для принудительного
завершения активной сессии пользователя, если он выполняет вход на новом АРМ.
Теперь можно отключить проверку целостности, выполняемую при запуске агента безопасности. Для
этого следует в файле alpha.security.ic.xml изменить значение нового атрибута
ICCheckOnAgentStartUp элемента Options:
«false» – для отключения первоначальной проверки целостности;
«true» – для включения первоначальной проверки целостности.
Исправления
Устранена причина, по которой не могли выполнять вход пользователи, учетные записи которых
были импортированы из Active Directory и имели кириллические имена.
Исправлена ошибка отображения имени текущего пользователя в сообщении аудита AUDIT_USER_
LOGON.
Агент безопасности теперь сообщает об ошибке при загрузке конфигурации неподходящего
формата. Ранее агент безопасности в таких случаях аварийно завершал работу.
Устранена причина, по которой заблокированный администратором пользователь разблокировался,
если истекала длительность его блокировки из-за неудачных попыток входа.
Решена проблема запуска агента безопасности на Astra Linux Orel: понижены требования к версии
glibc.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
163

=== Page 143 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
1.7.23
Улучшения
В файле с текстами сообщений аудита:
добавлен новый тег "arm.IP (N)", где N - порядковый номер интерфейса;
добавлено новое сообщение о неудачной попытке удаления учетной записи;
теперь можно использовать тег отображаемого имени в шаблонах "AUDIT_USER_FAILED_
LOGIN" и "AUDIT_USER_DISABLED_TEMP".
[только для SambaDC] В конфигурационный файл агента безопасности добавлен атрибут
OSAutoLogin элемента Options, позволяющий настроить автоматический вход системного
пользователя в подсистему безопасности.
Исправления
В сообщениях аудита, связанных с проверкой целостности, не отображалась группа пользователя.
Исправлен неинформативный текст ошибки, возникающей при неудачной попытке подключения к
LDAP-серверу.
Устранена причина, по которой права, назначенные пользователю, группе или роли, пропадали при
изменении их значений на те же самые.
Устранена причина, по которой новой учетной записи в процессе ее создания невозможно было
назначить роль.
Исправлен автоматический выход текущего пользователя при смене LDAP-сервера на
резервирующий.
1.7.25
Улучшения
Обновлены версии OpenLDAP и OpenSSL, поставляемых в составе дистрибутива Alpha.Security.
В файл alpha.security.agent.json добавлены новые шаблоны сообщений аудита:
об изменении отчества в учетных записях пользователей;
о добавлении роли новому пользователю.
В текст сообщения об ошибке соединения с сервером-потребителем сообщений аудита добавлена
информация об адресе и порте этого сервера.
Исправления
Устранена причина, по которой учетным записям, восстановленным из резервной копии
конфигурации, невозможно было добавить новые системные права, появившиеся в Alpha.Security 1.7.22
(NonDeletableWhileActive, ActivityLimitedToOneWorkstationOnly,
ForceStopOldUserSessionOnNewLogin).
Исправлено аварийное прекращение работы агента безопасности при попытке изменения значения
строкового права, хранящего настройки базы данных сервера истории.
Устранена причина, по которой не удавалось удалить учетную запись, если один из узлов домена
сети Alpha.Net был не доступен.
[Alpha.HMI.WebViewer] Пользователь, которому назначены права Только одна пользовательская
сессия и Принудительное завершение текущей пользовательской сессии при повторном входе, мог
иметь более одной активной сессии.
Устранены другие некритичные ошибки.
Включены изменения непубличной версии 1.7.24
164
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 144 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Важные изменения
Изменены механизм настройки и способ хранения конфигурации контроля целостности файлов и папок.
Ранее настройка выполнялась с помощью файлов alpha.security.agent.xml и alpha.security.ic.xml,
теперь конфигурация контроля целостности представляет собой зашифрованные файлы, расположенные в
папке:
C:\Program Files\Automiq\Alpha.Security\IC – для ОС Windows;
/opt/Automiq/Alpha.Security/IC – для ОС Linux.
Если для вашего агента безопасности ранее был настроен контроль целостности, то при установке
Alpha.Security версии 1.7.24 и новее разработанная в более ранних версиях конфигурация контроля
целостности автоматически преобразуется в новый формат. Чтобы изменить настройки контроля
целостности, следует создать проект Alpha.HMI, использующий расширение Alpha.HMI.Security версии
2.0.11 и новее. Расширение предоставит компонент Настройка безопасности: Контроль целостности,
позволяющий управлять настройками контроля целостности. Подробнее об этом – в документации на
Alpha.HMI.Security 2.0.12.
Улучшение
Добавлена возможность вывода отображаемого имени для шаблонов сообщений аудита "AUDIT_USER_
FAILED_LOGIN" и "AUDIT_USER_DISABLED_TEMP".
Исправления
Устранена причина, по которой невозможно было настроить разнонаправленное резервирование на
Astra Linux 1.8.1.
Устранена ошибка работы таймера пользовательской сессии при переводе системного времени
назад.
Устранена причина, по которой не выполнялась временная блокировка пользователя при превышении
количества неуспешных попыток входа.
[Alpha.HMI.Security] Исправлены ошибки подключения к каталогу на удаленном LDAP-сервере:
невозможность редактирования конфигурации каталога;
доступ к редактированию конфигурации заблокированного пользователя;
вход заблокированного пользователя.
1.7.26
Обратите внимание, эта версия совместима только с Alpha.HMI.Security 2.0.13.
Новая возможность
Добавлена возможность подключения к внешним источникам аутентификации для импорта учетных записей
из внешних источников в Alpha.Security. Для этого в конфигурационном файле агента безопасности
alpha.security.agent.xml следует указать данные внешнего источника аутентификации, шаблон для этих
данных добавлен в файл в виде комментариев. Импорт можно выполнить средствами расширения
Alpha.HMI.Security в собственном проекте Alpha.HMI, либо с помощью Alpha.HMI.SecurityConfigurator
2.5.0 и новее.
Исправления
Иногда после перезапуска АРМ не удавалось авторизоваться в подсистеме безопасности.
При смене пользователя операционной системы агент теперь обновляет информацию о текущем
пользователе. Ранее агент при смене пользователя операционной системы мог сохранять сессию
пользователя LDAP.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
165

=== Page 145 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Решена проблема некорректного завершения работы агента безопасности.
[Ред ОС 8] Устранена причина аварийного завершения работы службы агента безопасности,
связанного с исходной конфигурацией контроля целостности.
1.7.27
Исправления
Вместе с дистрибутивом теперь поставляется libssl.so.3. Из-за отсутствия этой библиотеки агент
безопасности ранее мог не запускаться.
Устранены причины аварийного завершения работы агента безопасности:
при попытке подключения к удаленному LDAP-серверу средствами Alpha.HMI.Security.
при попытке подключения к несуществующему LDAP-серверу (например, когда по ошибке
указан некорректный IP-адрес).
при попытке соединения с новым Alpha.Domain.Client, предназначенным для взаимодействия
сторонних приложений с компонентами Альфа платформы.
Исправлена ошибка, из-за которой иногда при перезапуске ОС агент безопасности не подключался к
LDAP-серверу, и, как следствие, не предоставлял ответы на запросы, отправленные средствами
Alpha.HMI.Security.
Устранена причина аварийного завершения работы Alpha.HMI при отправке команд контроля
целостности средствами Alpha.HMI.Security агенту безопасности.
Устранена причина, по которой иногда не удавалось сразу получить данные о только что
добавленных группах контроля целостности по запросу, отправленному средствами Alpha.HMI.Security.
Устранено ограничение на количество импортируемых одновременно учетных записей.
1.7.28
Улучшения
Добавлены новые системные права:
Проверка наличия пользовательских данных в пароле (PasswordNotContainUserData). Возможные
значения:
«true» – будет выполняться проверка наличия логина, имени, фамилии и отображаемого имени
пользователя в его пароле (без учёта регистра);
«false» – такая проверка выполняться не будет.
Время сохранения сессии пользователя при разрыве связи агента безопасности с хранилищем,
сек (UserSessionHoldTimeout). Здесь можно указать время (в секундах), в течение которого сохраняется
активность сессии пользователя при разрыве связи агента безопасности с LDAP-сервером.
Состав пароля (PasswordComposition). Позволяет ограничить набор доступных символов для пароля –
только цифры, только символы нижнего или верхнего регистра, только символы, либо сочетание
перечисленных ограничений.
Исправления
[Windows 11 PRO] Исправлено появление окна терминала фонового процесса при перезагрузке ОС.
Исправлен некорректный импорт доменного пользователя: создаваемая учетная запись либо не
добавлялась в группу, либо добавлялась в несколько групп одновременно.
Устранена причина, по которой активная сессия пользователя ошибочно не завершалась при
повторном входе пользователя.
166
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 146 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Дополнительная информация
Если агент безопасности работает некорректно, рекомендуем выполнить полное удаление Alpha.Security, а
затем установить новую версию повторно.
Изменения документации
Редакция 1
В раздел 2. Установка и удаление (стр. 7) добавлена команда удаления настроек и резервных копий
баз OpenLDAP в ОС Linux.
В описании настройки сообщений аудита для ОС Windows и OC Linux теперь упоминается
возможность задать этим сообщениям категорию важности.
В разделе 10. Решение распространенных проблем (стр. 122) описано, как изменить настройки
разнонаправленного резервирования OpenLDAP в ОС Linux (стр. 126).
В разделе «Настройка компонентов» -> «Для пользователей ОС Linux» удалено примечание о
необходимости вызова команды export |grep DISPLAY из директории
/opt/Automiq/Alpha.Security. Команду можно вызывать из любого расположения.
В Приложение B: SCAN-коды клавиш (стр. 133) исправлен ошибочно указанный код клавиши Esc:
значение «0x21» заменено на правильное – «0x01».
Редакция 2
Актуализировано описание настройки контроля целостности для ОС Windows и OC Linux. Здесь же
приведена расшифровка сообщений о результатах проверки целостности.
Обновлена схема взаимодействия компонентов Alpha.Security в разделе 1. О продукте (стр. 5).
Редакция 3
Добавлен недостающий закрывающий слеш в примерах xml-конструкций в разделах 6.7. Организация
кластерного рабочего места (стр. 103) и 7. Аудит безопасности (стр. 110).
Редакция 4
В разделе 2. Установка и удаление (стр. 7) актуализированы системные требования.
Раздел "Настройка компонентов" переименован в «Настройка компонентов Alpha.Security».
В раздел «Настройка компонентов» добавлен подраздел, описывающий настройку Агент
Alpha.Security и OpenLDAP «Для пользователей RPM-систем».
В подразделах, описывающих настройку агента безопасности:
Описано, как транслировать сообщения из системного журнала в сообщения аудита для
пользователей Debian-систем и для пользователей RPM-систем.
Упомянута необходимость импорта настроек модулей мониторинга для пользователей Debian-
систем и для пользователей RPM-систем. Без модулей мониторинга агент безопасности не будет
отслеживать длительность сессий и блокировок пользователей.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
167

=== Page 147 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
В подразделе, описывающем настройку агента безопасности для пользователей ОС Windows,
упомянута необходимость установки драйвера kbDriver. Драйвер необходим для корректной блокировки
использования сочетаний клавиш.
Редакция 5
В подразделах, описывающих «Настройка компонентов Alpha.Security» в части трансляции сообщений
аудита, описана возможность указывать:
звук, оповещающий о наступлении события определенной важности;
звук и необходимость квитирования для каждого события отдельно.
Редакция 6
Структура документа переработана:
Описание компонентов Alpha.Security из раздела 1. О продукте (стр. 5) перенесено в
собственные разделы: 3. LDAP-сервер и его настройка (стр. 11), 4. Агент безопасности и его
настройка (стр. 64), 6. Редактирование конфигурации на LDAP-сервере с помощью
SecurityConfigurator (стр. 73). Информация из бывшего раздела "Настройка компонентов
Alpha.Security" также перенесена в эти разделы.
Описание процесса подключения к LDAP-серверу из раздела 6. Редактирование конфигурации на
LDAP-сервере с помощью SecurityConfigurator (стр. 73) вынесено в собственный подраздел 6.1.
Подключение к LDAP-серверу из SecurityConfigurator (стр. 74).
Настройки и использование аудита безопасности и контроля целостности теперь описаны в
собственных подразделах 7. Аудит безопасности (стр. 110) и 8. Контроль целостности файлов и
папок (стр. 119). Ранее эти функции были описаны в разделах, описывающих настройку агента
безопасности.
В разделе 2. Установка и удаление (стр. 7) актуализированы системные требования.
В разделе 4. Агент безопасности и его настройка (стр. 64) описана возможность скрытия учетной
записи пользователя из запрашиваемого списка пользователей.
Редакция 7
Добавлены инструкции по работе с OpenLDAP для пользователей ОС семейства "Альт":
в раздел 2. Установка и удаление (стр. 7) добавлены команды установки и удаления;
добавлен отдельный раздел, описывающий настройку OpenLDAP (стр. 45).
Редакция 8
В раздел 10. Решение распространенных проблем (стр. 122) добавлена инструкция по настройке монитора
LDAP, которую следует выполнить, если в ОС Linux не работает временная блокировка пользователя.
Редакция 9
Обновлен раздел, описывающий настройку OpenLDAP 3.4. Для пользователей ОС семейства "Альт" (стр. 45):
Исправлена инструкция по настройке OpenLDAP. Ранее здесь было ошибочно указано, что
необходимо сначала создать и применить файл схемы, а после этого запустить сервис slapd.
168
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 148 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Правильнее сначала запустить сервис, а затем применять файл схемы.
Добавлена инструкция по настройке разнонаправленного резервирования LDAP-сервера.
Редакция 10
Актуализированы разделы 4. Агент безопасности и его настройка (стр. 64) и 6.1. Подключение к
LDAP-серверу из SecurityConfigurator (стр. 74). Информация в них обновлена с учетом того, что каталог
LDAP, указанный в настройках агента безопасности, теперь создается автоматически при первом
обращении к агенту.
В раздел, описывающий настройку LDAP-сервера 3.4. Для пользователей ОС семейства "Альт" (стр.
45), добавлена инструкция по настройке резервирования таким образом, чтобы не приходилось хранить
пароль администратора LDAP в конфигурационных файлах в открытом виде.
Актуализирован раздел 8. Контроль целостности файлов и папок (стр. 119).
Актуализировано Приложение D: Права системного приложения Alpha.Security (стр. 139). Здесь
описаны новые права и обновлена информация о вычислении эффективных значений прав.
Исправлены неверно указанные значения в Приложение B: SCAN-коды клавиш (стр. 133).
Редакция 11
Актуализирована инструкция по настройке LDAP-сервера 3.3. Для пользователей РЕД ОС (стр.
32): упомянута необходимость импорта настроек модуля мониторинга.
Актуализирован раздел 7. Аудит безопасности (стр. 110):
описано поведение агента безопасности в части аудита по умолчанию;
информация о типах сообщений аудита выделена в одноименный подраздел;
добавлен подраздел, описывающий способ полного отключения аудита безопасности.
Актуализирован раздел 8. Контроль целостности файлов и папок (стр. 119): здесь описаны новые
механизм настройки и способ хранения конфигурации контроля целостности файлов и папок.
В разделе 10. Решение распространенных проблем (стр. 122) описаны ошибки, связанные с
настройками аудита безопасности.
Редакция 12
Актуализированы инструкции по установке и настройке OpenLDAP 3.3. Для пользователей РЕД ОС (стр. 32),
3.4. Для пользователей ОС семейства "Альт" (стр. 45) и 3.2. Для пользователей DEB-систем (стр. 16). Также
в эти разделы добавлено упоминание правил формирования текстовых файлов, служащих для настройки
OpenLDAP.
Редакция 13
Актуализирована инструкция по настройке резервирования OpenLDAP3.2. Для пользователей DEB-
систем (стр. 16).
В разделе 4. Агент безопасности и его настройка (стр. 64) описана настройка подключения к внешним
источникам учетных данных (стр. 69).
Актуализирован пример файла alpha.security.agent.xml в Приложение A: Пример
конфигурационного файла Агент Alpha.Security (стр. 131).
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
169

=== Page 149 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Редакция 14
Добавлен новый раздел 3.5. Настройка SSL / TLS (для ОС Linux) (стр. 57). В разделе описано, как
создавать и применять собственные сертификаты для установления безопасного соединения с LDAP-
сервером, установленным в ОС Linux.
Актуализированы разделы, описывающие настройку LDAP-сервера:
3. LDAP-сервер и его настройка (стр. 11): более подробно описано, как функционирует OpenLDAP
в разных ОС.
3.1. Для пользователей Windows (стр. 12): описано, как изменить пароль администратора LDAP-
сервера.
3.2. Для пользователей DEB-систем (стр. 16): улучшена структура раздела; описано, как
изменить пароль администратора LDAP-сервера; приведен пример файла access.ldif,
применяемого для настройки политик контроля доступа.
3.3. Для пользователей РЕД ОС (стр. 32): исправлены ошибки инструкции; улучшена структура
раздела; описано, как изменить пароль администратора LDAP-сервера; приведен пример файла
access.ldif, применяемого для настройки политик контроля доступа.
3.4. Для пользователей ОС семейства "Альт" (стр. 45): улучшена структура раздела; описана
разница в настройке LDAP-сервера для Alt Linux 10 и Alt Linux 11.
В разделе 5. Запуск сервисов (для ОС Linux) (стр. 70) расширена инструкция по настройке и запуску
сервисов агента безопасности от имени непривилегированного пользователя.
В разделе 8. Контроль целостности файлов и папок (стр. 119) описано, как полностью отключить
контроль целостности.
Редакция 15
Актуализирована таблица системных прав в Приложение D: Права системного приложения
Alpha.Security (стр. 139).
Добавлено новое Приложение E: Сообщения аудита (стр. 144) – здесь приведена расшифровка
текстов сообщений аудита для упрощения их понимания.
Редакция 16
В разделы, описывающие настройку LDAP-сервера 3.2. Для пользователей DEB-систем (стр. 16) и
3.3. Для пользователей РЕД ОС (стр. 32), добавлена инструкция по смене логина и пароля
администратора LDAP-сервера (ранее была описана инструкция только для смены пароля
администратора).
Исправлено дублирование информации в разделе, описывающем настройку LDAP-сервера 3.2. Для
пользователей DEB-систем (стр. 16)
1.6
1.6.5
Улучшения
170
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 150 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Ускорено выполнение контроля целостности для большого количества файлов.
Теперь каждому сообщению аудита можно задать категорию важности. Сообщения и их категории
важности описываются в файле alpha.security.agent.json, расположенном в папке установки
Alpha.Security.
Исправления
Устранена причина, по которой пропадало соединение Alpha.HMI с Агент Alpha.Security. Проблема
возникала после выхода и повторного входа пользователя в ОС, с последующей сменой пользователя
Alpha.Security из проекта Alpha.HMI.
Решена проблема, из-за которой в ОС Linux не происходил автоматический выход пользователя из
подсистемы безопасности по истечении:
времени блокировки при превышении количества неуспешных попыток входа;
максимального времени бездействия пользователя.
Изменения документации
Редакция 1
В разделе «Настройка компонентов» -> «Для пользователей ОС Linux»:
Исправлен текст конфигурационных файлов, предназначенных для настройки резервирования
OpenLDAP на Linux: для отступа от левого края в строках необходимо использовать два пробела вместо
одного.
Исправлена неверно указанная команда перезапуска сервиса Alpha.Security на Linux.
Было: sudo systemctl restart Alpha.Security.
Стало: sudo systemctl restart alpha.security.service.
В разделе «Редактирование конфигурации на LDAP-сервере с помощью SecurityConfigurator»:
Описана настройка запуска конфигуратора без ввода пароля при наличии активной пользовательской
сессии (см. Подключение к LDAP-серверу с помощью агента безопасности (стр. 77)).
Описан процесс установки безопасного соединения при подключении к LDAP-серверу (стр. 78).
Описана возможность изменения начальных значений прав, добавляемых пользователю
автоматически при создании учетной записи (см. Изменить начальные значения прав на уровне
приложения (стр. 94)).
Добавлен новый раздел 10. Решение распространенных проблем (стр. 122).
Редакция 2
В разделе «Настройка компонентов»:
Приведены новые параметры описания сервера-потребителя сообщений аудита HostTcpReserve и
MasterPasswordCipher – для пользователей Windows и для пользователей Linux.
Описана настройка списка файлов, целостность которых должна контролироваться подсистемой
безопасности – для пользователей Windows и для пользователей Linux. Теперь из списка можно
исключать вложенные файлы и папки, а также фильтровать контролируемые файлы и папки по
расширению или названию.
Для пользователей ОС Linux описана настройка сервиса Alpha.Security, предназначенного для
отслеживания длительности сессий и времени бездействия пользователей.
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
171

=== Page 151 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Редакция 3
В разделе «Настройка компонентов» -> «Для пользователей ОС Linux»:
описана настройка OpenLDAP, применяемая для отслеживания длительности сессий и блокировок
пользователей – импорт настроек модуля мониторинга;
описана возможность запуска сервисов агента безопасности от имени непривилегированного
пользователя.
В разделе 10. Решение распространенных проблем (стр. 122) описано, как предотвратить появление в
журнале сообщений вида <= mdb_equality_candidates: (xxx) not indexed.
Во всем документе актуализированы скриншоты.
1.5
Важно. Текущая версия предназначена для использования с Alpha.HMI 1.10.
Изменения документации
Редакция 1
В разделе «Настройка компонентов»:
Описано, как исключать из контроля целостности вложенные в контролируемую папку файлы и
папки:
для Windows;
для Linux.
Исправлен неверно указанный путь к файлу конфигурации OpenLDAP в подразделах, описывающих
настройку резервирования для Windows. Неправильный путь – C:\Program Files\OpenLDAP (папка
установки OpenLDAP), правильный – C:\ProgramData\OpenLDAP\openldap.
В подраздел, описывающий настройку OpenLDAP для Linux, добавлено упоминание о необходимости
выполнения всех команд от имени суперпользователя root.
В разделе «Редактирование конфигурации на LDAP-сервере с помощью SecurityConfigurator»:
В подразделе 6.5. Создание и редактирование учетных записей (стр. 89) добавлено примечание о
защите паролей создаваемых учетных записей.
Исправлена ошибка в описании настройки Агент Alpha.Security при создании кластерного рабочего
места (стр. 103). Для агентов дочерних узлов сети Alpha.Net необходимо указывать параметры
локальной точки доступа Net-агента, а не центральной.
В Приложение B: SCAN-коды клавиш (стр. 133) актуализирован SCAN-код клавиши PrtSc: значение «0х137»
заменено на «0x54».
1.4
172
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 152 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Изменения документации
Редакция 1
Добавлен раздел «Подготовка к работе», описывающий:
системные требования для всех компонентов подсистемы Alpha.Security;
процесс установки компонентов Alpha.Security для ОС Windows и Linux.
Редакция 2
Обновлен раздел «Подготовка к работе»:
детализировано описание настройки OpenLDAP для ОС Linux;
описан процесс резервирования OpenLDAP для ОС Windows и Linux.
Редакция 3
Структура документа полностью переработана:
Информация из бывшего раздела «Подготовка к работе» описана более подробно и разнесена по
новым разделам: «Установка и удаление» и «Настройка компонентов». Для удобства настройка
компонентов описана для разных операционных систем по отдельности.
Описание работы в SecurityConfigurator (создание и редактирование учетных записей, групп и т.д.)
переработано и сгруппировано в раздел «Редактирование конфигурации на LDAP-сервере с помощью
SecurityConfigurator». Новое в разделе:
описана возможность создания трех типов учетных записей;
описана возможность блокировки учетных записей и групп;
актуализированы скриншоты.
Описана настройка трансляции сообщений аудита – в разделе «Настройка компонентов», и приведен
пример использования функции аудита – в разделе 7. Аудит безопасности (стр. 110).
Информация из бывшего подраздела «Сервис безопасности в приложениях» вынесена в
самостоятельный раздел 9. Безопасность в компонентах Альфа платформы (стр. 120).
ПОДСИСТЕМА ALPHA.SECURITY. РУКОВОДСТВО АДМИНИСТРАТОРА
173

=== Page 153 ===
Программный комплекс Альфа платформа
Alpha.AccessPoint 6.4
Руководство администратора
Редакция
Соответствует версии ПО
7. Предварительная
6.4.28

=== Page 154 ===
© АО «Атомик Софт», 2015-2026. Все права защищены.
Авторские права на данный документ принадлежат АО «Атомик
Софт». Копирование, перепечатка и публикация любой части или
всего документа не допускается без письменного разрешения
правообладателя.

=== Page 155 ===
Содержание
1. Назначение и принцип работы
4
1.1. Поддержание связи с источниками
5
1.2. Alpha.AccessPoint в TCP/IP сетях
7
2. Подготовка к работе
9
2.1. Системные требования
9
2.2. Установка
10
2.3. Управление Alpha.AccessPoint
11
2.4. Тиражирование Alpha.AccessPoint
12
2.5. Удаление
12
3. Настройка
14
3.1. Подключение к Alpha.AccessPoint и общие настройки
14
3.2. Настройка источников
16
3.3. Настройка серверов источника
19
3.4. Настройка каналов
20
3.5. Настройка привязок ветвей сигналов
22
3.6. Настройка привязок статических сигналов
24
3.7. Передача данных через файловый интерфейс
26
3.8. Защита от несанкционированного доступа
28
4. Получение данных от Alpha.AccessPoint
29
4.1. Получение оперативных значений сигналов по OPC DA
29
4.2. Получение оперативных событий по OPC AE
29
4.3. Получение оперативных данных по OPC UA
30
4.4. Получение исторических данных по OPC UA
33
5. Пример настройки
37
6. Диагностика работы
40
Список терминов и сокращений
42
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА
3

=== Page 156 ===
1. НАЗНАЧЕНИЕ И ПРИНЦИП РАБОТЫ
1. Назначение и принцип работы
Alpha.AccessPoint выполняет роль конечной точки доступа к оперативным данным и событиям множества
источников данных.
Основные возможности Alpha.AccessPoint:
объединение сигналов различных источников в единое дерево сигналов (стр. 29);
объединение событий и тревог от различных источников (стр. 29);
поддержание связи с источниками данных при разрыве соединения (стр. 5);
передача значений и событий в виде TCP/IP-трафика в условиях различных сетевых топологий и
работа в режиме каскадирования (стр. 7);
поддержка сбора данных по файловому интерфейсу (стр. 26);
доступ к данным Alpha.AccessPoint выполняется по спецификациям OPC DA, OPC AE, OPC UA
(стр. 29).
ОБРАТИТЕ ВНИМАНИЕ
Спецификации OPC DA и OPC AE базируются на COM/DCOM и используются только в ОС Windows.
Принцип работы:
1. Alpha.AccessPoint соединяется и поддерживает связь с источниками данных:
сканирует, а затем активирует найденные каналы связи в составе источника данных;
определяет, какой из серверов в составе источника данных является активным;
выбирает рабочий канал и активирует сеанс передачи данных;
применяет алгоритмы поддержания связи при потере соединения с источником (стр. 5).
2. Alpha.AccessPoint формирует общее адресное пространство в соответствии с настройками привязок
ветвей (стр. 22) или статических сигналов (стр. 24).
3. OPC DA-клиенты подключаются к Alpha.AccessPoint и подписываются на сигналы общего адресного
пространства (только в ОС Windows) (стр. 29).
4. OPC AE-клиенты подключаются к Alpha.AccessPoint, как к единой точке приёма AE-уведомлений
(только в ОС Windows) (стр. 29).
5. OPC UA-клиенты подключаются к Alpha.AccessPoint, как к единой точке приёма оперативных
значений и событий, а также источнику исторических данных (стр. 30).
6. В неоднородных сетевых топологиях применяется режим каскадирования, когда несколько
экземпляров Alpha.AccessPoint соединяются между собой (стр. 7).
4
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 157 ===
1. НАЗНАЧЕНИЕ И ПРИНЦИП РАБОТЫ
1.1. Поддержание связи с источниками
Alpha.AccessPoint обладает встроенной логикой переключения между серверами и каналами источника
данных при разрыве соединения. Некоторые особенности алгоритма поддержания связи:
Alpha.AccessPoint автоматически проводит инициализацию всех указанных каналов связи (стр. 20),
а затем определяет активный сервер (стр. 19) в составе источника данных (стр. 16). Существует
несколько алгоритмов определения активного сервера;
в случае разрыва соединения Alpha.AccessPoint пытается восстановить связь через резервные
каналы активного сервера, если такие имеются;
если не удалось восстановить связь по резервным каналам активного сервера, то Alpha.AccessPoint
переключается на работу с резервным сервером.
Пример процесса поддержания связи с источником
Источник состоит из двух серверов, работающих в режиме горячего резервирования.
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА
5

=== Page 158 ===
1. НАЗНАЧЕНИЕ И ПРИНЦИП РАБОТЫ
Пример процесса поддержания связи с источником
Источник состоит из двух серверов, которые работают по схеме дублирования.
6
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 159 ===
1. НАЗНАЧЕНИЕ И ПРИНЦИП РАБОТЫ
1.2. Alpha.AccessPoint в TCP/IP сетях
Применение Alpha.AccessPoint обеспечит проект автоматизации следующими преимуществами:
в качестве источника данных может выступать как Alpha.Server, так и сам Alpha.AccessPoint
(режим каскадирования, на схеме ниже - Alpha.AccessPoint 3 работает в режиме каскадирования). Такая
схема построения удобна, когда проект автоматизации развернут в нескольких подсетях;
Alpha.AccessPoint выполняет роль сервера-приложений, который ограничивает нагрузку,
создаваемую множеством клиентов при прямых подключениях к серверам;
Alpha.AccessPoint обеспечивает высокую скорость обмена данными и простую методику
конфигурирования в условиях неоднородной сетевой топологии благодаря использованию протокола на
базе TCP/IP.
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА
7

=== Page 160 ===
1. НАЗНАЧЕНИЕ И ПРИНЦИП РАБОТЫ
8
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 161 ===
2. ПОДГОТОВКА К РАБОТЕ
2. Подготовка к работе
2.1. Системные требования
Системные требования компьютеров для установки Alpha.AccessPoint:
ОС
Microsoft Windows 10 Pro/11 Pro
Microsoft Windows Server 2012/2012 R2/2016/2019/2022
Astra Linux, РЕД ОС, Ubuntu, ОС семейства "Альт" (glibc не ниже 2.17)
Разрядность
ОС
x64
Процессор
Intel Celeron с тактовой частотой не менее 1.6 ГГц
Объем
оперативной
памяти
не менее 2 ГБ
Объем
дисковой
памяти
не менее 1 ГБ
Сетевой
адаптер
Ethernet 10/100/1000 Мбит/с
Установленное
ПО
Для OC Windows:
Антивирусное ПО
OPC Core Components версии 105.1 (ссылка для скачивания:
https://opcfoundation.org/developer-tools/samples-and-tools-classic/core-components)
Системные требования компьютеров для установки клиентской части Alpha.AccessPoint:
ОС
Microsoft Windows 10 Pro/11 Pro
Microsoft Windows Server 2012/2012 R2/2016/2019/2022
Разрядность
ОС
x64
Процессор
Intel Celeron с тактовой частотой не менее 1.6 ГГц
Объем
оперативной
памяти
не менее 1 ГБ
Объем
дисковой
памяти
не менее 500 МБ
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА
9

=== Page 162 ===
2. ПОДГОТОВКА К РАБОТЕ
Сетевой
адаптер
Ethernet 10/100/1000 Мбит/с
Установленное
ПО
Антивирусное ПО
.NET 4.6.1 (ссылка для скачивания: https://www.microsoft.com/ru-
ru/download/details.aspx?id=49982)
OPC .NET API 2.00 Redistributables 105.0 (ссылка для скачивания:
https://opcfoundation.org/developer-tools/samples-and-tools-classic/net-api-sample-client-
source-code)
2.2. Установка
ОС Windows
ОБРАТИТЕ ВНИМАНИЕ
Для установки Alpha.AccessPoint следует выполнить вход в систему с правами администратора ОС.
Для установки Alpha.AccessPoint:
1. Запустите дистрибутив Alpha.AccessPoint-x.x.x+xx.xxxxx (x64).msi.
2. Следуйте указаниям мастера установки.
3. После завершения установки Alpha.AccessPoint начнет функционировать в виде службы
Alpha.AccessPoint.
Alpha.AccessPoint устанавливается в каталог по умолчанию C:\Program
Files\Automiq\Alpha.AccessPoint\Server.
В состав дистрибутива Alpha.AccessPoint входят сервисные приложения:
Конфигуратор. Для запуска выполните команду: Пуск →Automiq →Конфигуратор.
Статистика. Для запуска выполните команду: Пуск →Automiq →Статистика.
Просмотрщик лога кадров. Для запуска выполните команду: Пуск →Automiq →Просмотрщик лога
кадров.
Сервисные приложения устанавливаются в каталог по умолчанию C:\Program
Files\Automiq\Alpha.AccessPoint\Service.
ОБРАТИТЕ ВНИМАНИЕ
Настройка Alpha.AccessPoint выполняется в сервисном приложении Конфигуратор. Для
подключения используется порт «4976».
ОС Linux
Установка выполняется штатным пакетным менеджером. Сервисные приложения не устанавливаются.
ОБРАТИТЕ ВНИМАНИЕ
Команда установки выполняется только от суперпользователя «root».
10
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 163 ===
2. ПОДГОТОВКА К РАБОТЕ
Имя устанавливаемого пакета: alpha.accesspoint-x.x.x+xx.xxxxx.deb или alpha.accesspoint-
x.x.x+xx.xxxxx.rpm в зависимости от используемой ОС Linux.
Установка пакета *.rpm с помощью пакетного менеджера YUM:
yum install alpha.accesspoint-x.x.x+xx.xxxxx.rpm
Установка пакета *.rpm с помощью пакетного менеджера RPM:
rpm -i alpha.accesspoint-x.x.x+xx.xxxxx.rpm
Установка пакета *.deb с помощью пакетного менеджера apt:
apt-get install alpha.accesspoint-x.x.x+xx.xxxxx.deb
Установка пакета *.deb с помощью пакетного менеджера dpkg:
dpkg -i alpha.accesspoint-x.x.x+xx.xxxxx.deb
После завершения установки Alpha.AccessPoint начнет функционировать в виде сервиса alpha.accesspoint.
Alpha.AccessPoint устанавливается в директорию /opt/Automiq/Alpha.AccessPoint.
2.3. Управление Alpha.AccessPoint
ОС Windows
Управление Alpha.AccessPoint выполняется путем запуска/перезапуска/останова службы Alpha.AccessPoint
стандартными инструментами ОС Windows.
ОС Linux
Управление Alpha.AccessPoint выполняется путем запуска/перезапуска/останова сервиса alpha.accesspoint
специализированными командами.
ОБРАТИТЕ ВНИМАНИЕ
Все команды выполняются только от суперпользователя «root».
Запуск:
systemctl start alpha.accesspoint
Останов:
systemctl stop alpha.accesspoint
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА
11

=== Page 164 ===
2. ПОДГОТОВКА К РАБОТЕ
Перезапуск:
systemctl restart alpha.accesspoint
2.4. Тиражирование Alpha.AccessPoint
Для переноса, сконфигурированного Alpha.AccessPoint на другую машину без использования установочного
дистрибутива, нужно выполнить следующие действия:
убедиться, что целевая машина соответствует системным требованиям (стр. 9);
остановить работающую службу Alpha.AccessPoint;
скопировать папку C:\Program Files\Automiq\Alpha.AccessPoint по аналогичному пути на другой
машине;
зарегистрировать службу Alpha.AccessPoint на другой машине (из командной строки):
C:\Program Files\Automiq\Alpha.AccessPoint\Server\Alpha.AccessPointInstaller.exe
/install
убедиться в успешной регистрации службы, проверив её активность в списке служб ОС Windows.
2.5. Удаление
ОС Windows
Удаление Alpha.AccessPoint и вспомогательного ПО выполняется стандартными инструментами:
1. Запустить программу Программы и компоненты: Пуск →Панель управления →Программы и
компоненты.
2. В списке установленных программ выбрать Alpha.AccessPoint и нажать кнопку Удалить.
При удалении Alpha.AccessPoint также выполняется удаление установленных сервисных приложений.
Если Alpha.AccessPoint был тиражирован без использования установочного дистрибутива (стр. 12), то для
его корректного удаления нужно выполнить следующие действия:
разрегистрировать службу Alpha.AccessPoint (из командной строки):
C:\Program Files\Automiq\Alpha.AccessPoint\Server\Alpha.AccessPointInstaller.exe
/uninstall
убедиться в успешной разрегистрации службы, проверив её отсутствие в списке служб ОС Windows;
вручную удалить папку C:\Program Files\Automiq\Alpha.AccessPoint.
ОС Linux
Удаление Alpha.AccessPoint выполняется штатным пакетным менеджером.
ОБРАТИТЕ ВНИМАНИЕ
Команда удаления выполняется только от суперпользователя «root».
12
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 165 ===
2. ПОДГОТОВКА К РАБОТЕ
Удаление с помощью пакетного менеджера YUM:
yum remove alpha.accesspoint
Удаление с помощью пакетного менеджера RPM:
rpm -e alpha.accesspoint
Удаление пакета *.deb с помощью пакетного менеджера apt:
apt-get remove alpha.accesspoint
Удаление пакета *.deb с помощью пакетного менеджера dpkg:
dpkg -r alpha.accesspoint
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА
13

=== Page 166 ===
3. НАСТРОЙКА
3. Настройка
3.1. Подключение к Alpha.AccessPoint и общие настройки
Все настройки Alpha.AccessPoint производятся с помощью сервисного приложения Конфигуратор, которое
входит в состав дистрибутива. Конфигуратор запускается из меню Пуск →Automiq →Alpha.AccessPoint →
Конфигуратор.
Чтобы создать новое подключение к серверу, нажмите кнопку
(Подключиться к серверу) на панели
инструментов или выполните команду меню Сервер →Подключиться к серверу…. В открывшемся окне
Подключение к серверу укажите параметры подключения:
Параметр
Описание
Название
Название подключения (для отображения в списках подключений)
IP-адрес
Сетевой адрес компьютера с установленным сервером
Порт
Номер порта для подключения к серверу
Пароль
Пароль доступа к экземпляру сервера.
ОБРАТИТЕ ВНИМАНИЕ
При первом подключении к серверу, если пароль доступа еще не задан, поле Пароль оставьте
пустым.
Чтобы в список Подключения добавить новые серверы, нажмите кнопку Добавить и укажите параметры
подключения.
Чтобы подключиться к серверу из списка Последних подключений, выполните команду меню Сервер →
Последние подключения, или нажмите стрелку рядом с кнопкой
(Подключиться к серверу) , и выберите
сервер для подключения.
14
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 167 ===
3. НАСТРОЙКА
По умолчанию для подключения к Alpha.AccessPoint используется порт «4976».
В таблице приведены модули Alpha.AccessPoint.
Модуль
Поддержка в ОС
Windows
Linux
HUB Module
ü
ü
TCP Server Module
ü
ü
OPC AE Server
ü
ü
OPC UA
ü
ü
History Module
ü
ü
OPC DA Server
ü
OPC HDA Server
ü
OPC HDA Client
ü
Источники данных, с которыми будет работать Alpha.AccessPoint, добавляются через HUB Module.
Общие параметры HUB Module:
Параметр
Описание
Имя модуля
Название модуля. По умолчанию «HUB Module»
Идентификатор
модуля
Идентификатор модуля в Alpha.AccessPoint
Активность
Активность модуля:
«Да» – модуль запущен
«Нет» – модуль остановлен
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА
15

=== Page 168 ===
3. НАСТРОЙКА
Параметр
Описание
Уровень
трассировки в
журнал
приложений
Типы сообщений, которые фиксируются в журнал приложений:
«Предупреждения и аварийные сообщения» – логические ошибки, ошибки работы
модуля Alpha.AccessPoint. Предупреждения содержат некритичные ошибки.
Аварийные сообщения информируют об ошибках, которые влияют на
работоспособность Alpha.AccessPoint;
«Информационные сообщения» – сообщения, которые показывают основную
информацию о работе модуля;
«Отладочные сообщения» – сообщения, которые наиболее детально отражают
информацию о работе модуля.
Вышестоящий уровень входит в состав нижестоящего. Если установлен уровень
«Информационные сообщения», то в журнал фиксируются «Предупреждения и аварийные
сообщения» и «Информационные сообщения»
Вести журнал
работы модуля
Параметр, показывающий ведется ли запись сообщений о работе модуля в журнал
работы модуля:
«Да» – сведения о работе модуля сохраняются в журнал
«Нет» – журнал работы модуля не ведётся
Размер журнала
работы модуля,
МБ
Размер файла журнала работы модуля в мегабайтах. При достижении максимального
размера создается новый файл, копия старого файла хранится на рабочем диске
Количество
дополнительных
журналов
работы
Количество файлов заполненных журналов работы модуля. Минимальное значение
параметра равно «1». Максимальное количество файлов журнала равно «255».
Для того, чтобы новые параметры HUB Module вступили в силу, следует перезапустить Alpha.AccessPoint
(стр. 11).
3.2. Настройка источников
HUB Module в составе Alpha.AccessPoint предназначен для настройки подключения к источникам данных.
Из сигналов источников будет строиться объединенное адресное пространство Alpha.AccessPoint. Для
добавления источников выберите элемент дерева Источники, а затем нажмите на кнопку
.
В окне Источники можно добавлять, редактировать и удалять источники данных.
16
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 169 ===
3. НАСТРОЙКА
Основные параметры источника:
Параметр
Описание
Алгоритм
определения
активного сервера
Способ определения активного сервера в составе источника:
«Любой работоспособный» - при потере связи модуль пытается установить
соединение с любым работоспособным сервером в составе источника;
«Первый по порядку» - модуль работает с первым сервером в приоритетном
порядке. При потере связи с первым сервером, модуль установит соединение с
любым работоспособным сервером в составе источника, но не прекратит
попыток восстановить связь с первым сервером. Как только связь с первым
сервером будет восстановлена, модуль возобновит с ним работу. Чтобы
определить порядок серверов, воспользуйтесь стрелками в окне Серверы (стр.
19);
«Первый запущенный» - модуль выбирает для работы тот сервер в составе
источника, время запуска которого было раньше
Алгоритм
определения
работоспособности
сервера
Способ проверки работоспособности серверов в составе источника:
«По статусу» - по ответу на запрос к серверу специальным методом
GetStatus. Значение dwServerState = OPC_STATUS_RUNNING означает, что сервер
находится в работе;
«По качеству» - по качеству контрольного сигнала. Если качество
контрольного сигнала < 192, то связь с сервером потеряна. Если качество
сигнала равно 192, то сервер работоспособен;
«По значению» - по значению контрольного сигнала. Указывается значение
сигнала, при котором считается, что сервер работоспособен. При других
значениях сигнала связь с источником потеряна
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА
17

=== Page 170 ===
3. НАСТРОЙКА
Параметр
Описание
Записывать во все
сервера
Параметр активирует запись значений сигналов в оба сервера источника данных (в
активный и в резервный). По умолчанию значение «Нет» - запись производится
только в активный сервер источника. Значение «Да» может быть полезно, когда не
возможна синхронизация значений сигналов между активным и резервным
серверами источника
Значение
контрольного
сигнала
Параметр предназначен для указания значения контрольного сигнала, при котором
сервер считается работоспособным
Идентификатор
клиента
Параметр идентифицирует клиент Alpha.AccessPoint для модуля TCP Server
Module на стороне источника
Имя
Однозначно идентифицирует источник данных в дереве настроек HUB Module и в
журнале работы
Контрольный
сигнал
Параметр предназначен для указания тега сигнала, который будет считаться
контрольным для определения работоспособности сервера
Таймаут потери
связи, мсек
Период времени, после превышения которого связь с источником данных считается
потерянной. По умолчанию равен «1000» мсек. Отсчет таймаута начинается с
момента, когда все каналы источника данных перестают отвечать на запросы
Alpha.AccessPoint
Группа параметров Периодическое обновление дерева отвечает за то, с какой интенсивностью
Alpha.AccessPoint будет опрашивать источники данных. Обновления от источников приходят в
Alpha.AccessPoint в виде группы пакетов, внутри которых содержатся сигналы. Ниже описаны параметры,
настройка которых позволяет найти нужное сочетание скорости и нагрузки на источник данных в ходе
выполнения запросов.
Параметр
Описание
Обновлять
всегда
Если параметр активен, то происходит постоянное циклическое обновление дерева
источника с определенными паузами (параметр Пауза между процедурами при обновлении
дерева, сек). Если параметр неактивен, то конфигурация обновится единожды - при
подключении Alpha.AccessPoint к источнику данных. Активность этого параметра имеет
смысл только при использовании нескольких Alpha.AccessPoint в режиме каскадирования
(стр. 7)
Пауза между
процедурами
при
обновлении
дерева, сек
Период простоя, перед следующим обновлением конфигурации источника. Малые паузы
между обновлениями повышают актуальность дерева сигналов источника, но увеличивает
нагрузку на источник данных за счет более частых запросов. По умолчанию – «60» секунд
Максимальное
количество
сигналов в
пакете
Параметр определяет вместимость каждого пакета с сигналами дерева. Большие пакеты
сигналов ускорят процесс обновления дерева, но повысят нагрузку на сервер-источник. По
умолчанию «10000» сигналов в пакете
18
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 171 ===
3. НАСТРОЙКА
Параметр
Описание
Период
отправки
пакетов
Время, отведенное источнику, за которое он должен отправить один пакет с сигналами.
Малое значение параметра ускорит процесс обмена данными, но увеличит нагрузку на
сервер за счет более интенсивной отправки пакетов. Параметр измеряется в
миллисекундах. По умолчанию «1000» мсек.
ВАЖНО
Если источник данных защищен от несанкционированного обмена данными с Alpha.AccessPoint, то
для подключения к источнику потребуется ввод пароля. Укажите пароль доступа к источнику во всех
узлах конфигурирования каналов источника, в настройках HUB Module.
Пример настройки периодического обновления дерева
Пусть нужно настроить периодическое обновление конфигурации некоего источника с интервалом в 15
секунд. Во время каждого опроса дерева, данные должны поступать от источника небольшими пакетами (по
50 сигналов), с периодичностью 15 секунд. Для данного примера, временная шкала процесса обновления
дерева показана на рисунке ниже.
Для решения данной задачи нужно установить настройки источника, как показано на рисунке ниже.
Группа параметров Настройки файлового интерфейса описана ниже (стр. 26).
ВАЖНО
Если источник данных защищен от несанкционированного обмена данными с Alpha.AccessPoint, то
для подключения к источнику потребуется ввод пароля. Укажите пароль доступа к источнику во всех
узлах конфигурирования каналов источника, в настройках HUB Module.
3.3. Настройка серверов источника
Каждый источник данных может включать в свой состав несколько серверов, которые могут работать, как в
режиме горячего резервирования, так и в режиме дублирования. Для конфигурирования серверов источника
данных нужно выбрать узел дерева Серверы, а затем нажать кнопку
.
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА
19

=== Page 172 ===
3. НАСТРОЙКА
В окне Серверы можно добавлять, редактировать и удалять серверы источника данных.
Единственным настраиваемым параметром сервера является его имя, которое будет однозначно
идентифицировать сервер в дереве настроек HUB Module и в журналах работы.
3.4. Настройка каналов
Каждый сервер источника данных может содержать несколько каналов связи. В целях резервирования и
повышения надежности каналы работают по разным физическим линиям передачи данных и имеют разные
сетевые адреса. IP-адреса каналов и их порты задаются администратором на стороне источника данных и
должны быть заранее известны администратору Alpha.AccessPoint. Для конфигурирования каналов нужно в
дереве HUB Module выбрать элемент Каналы, а затем нажать кнопку
.
20
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 173 ===
3. НАСТРОЙКА
В окне Каналы можно добавлять, редактировать и удалять каналы сервера, а также указывать пароль, если
источник был защищен от несанкционированного обмена данными.
Параметр
Описание
IP адрес
Уникальный сетевой адрес канала связи в пределах сегмента сети
Имя
Название канала, однозначно идентифицирует канал в составе сервера
Максимальное
количество
сигналов в
команде
Параметр ограничивает максимальное количество сигналов, на которые можно
подписаться в рамках одной команды
Пароль
Пароль для обмена данными с источником указывается, если серверы источника
защищены от несанкционированного обмена данными с Alpha.AccessPoint
ОБРАТИТЕ ВНИМАНИЕ
Пароль хранится в файле конфигурации в зашифрованном виде.
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА
21

=== Page 174 ===
3. НАСТРОЙКА
Параметр
Описание
Порт
Уникальный идентификатор сетевого процесса в пределах машины. Должен
соответствовать порту TCP Server Module установленному на источнике данных
Alpha.Server. По умолчанию «4388»
Таймаут
операции, мсек
Период времени в миллисекундах после которого связь с каналом считается
потерянной. Отсчет таймаута начинается с момента, когда источник перестает отвечать
на запросы Alpha.AccessPoint по данному каналу связи. По умолчанию: «1000» мсек.
3.5. Настройка привязок ветвей сигналов
Привязки используются для построения объединенного адресного пространства Alpha.AccessPoint, которое
формируется путем слияния адресных пространств различных источников. При этом могут объединяться как
целые деревья, так и отдельные их ветви.
Параметры привязки:
Параметр
Описание
Имя
Название привязки
Папка
приемник
Ветвь адресного пространства Alpha.AccessPoint, в которую будет включена ветвь
адресного пространства источника, указанная в параметре Папка источник
Папка
источник
Ветвь адресного пространства источника, сигналы которой будут включены в общее
адресное пространство Alpha.AccessPoint
Постоянная
подписка
Определяет момент подписки на сигналы из ветви адресного пространства источника,
указанной в параметре Папка источник:
«Да» - подписка на сигналы происходит при запуске модуля HUB;
«Нет» - подписка на сигналы происходит только когда к Alpha.AccessPoint
подключается клиент.
Чтобы повлиять на порядок построения общего дерева сигналов, воспользуйтесь кнопками стрелок, которые
задают приоритет при построении дерева. Чем выше стоит привязка в списке, тем раньше сигналы по этой
привязки будут включены в общее дерево.
22
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 175 ===
3. НАСТРОЙКА
Пример настройки привязок
Пусть требуется объединить деревья трех источников данных («Root_1», «Root_2», «Root_3») в общее
адресное пространство Alpha.AccessPoint со структурой, как на рисунке ниже.
Этапы конфигурирования привязок для выполнения данной задачи.
1. Для источника данных «Root_1» создать две привязки (как на рисунках ниже). В первом случае в папку
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА
23

=== Page 176 ===
3. НАСТРОЙКА
приемник перекладывается всё дерево «Root_1». Во втором случае перекладывается только ветка
«Folder_A1».
2. Для источника данных «Root_2» создать привязку, показанную ниже.
3. Для источника данных «Root_3» создать привязку, показанную ниже. В этом случае указывается
конкретный путь общего адресного пространства, в которое будет перекладываться дерево «Root_3».
3.6. Настройка привязок статических сигналов
Чтобы включить в адресное пространство Alpha.AccessPoint отдельный (статический) сигнал источника
данных (без использования привязок) добавьте нужный сигнал через Конфигуратор и настройте для него
свойство 5000 в Редакторе адреса.
ОБРАТИТЕ ВНИМАНИЕ
Статическая привязка сигналов также используется для связи источника и Alpha.AccessPoint в
режиме файлового интерфейса (стр. 26).
24
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 177 ===
3. НАСТРОЙКА
Чтобы создать статическую привязку сигнала, в Редакторе адреса для свойства 5000 укажите:
Идентификатор HUB Module.
Один из источников данных, созданных в процессе конфигурирования источников (стр. 16).
Идентификатор конфигурации источника (можно узнать в сигнале источника с тегом
«Service.Id.Str»).
Идентификатор сигнала, который можно узнать, сохранив конфигурацию источника в формате
*.xmlcfg и открыв её в текстовом редакторе.
При построении общего адресного пространства Alpha.AccessPoint, механизм привязки статических
сигналов имеет приоритет перед механизмом привязки ветвей (стр. 22).
ОБРАТИТЕ ВНИМАНИЕ
При построении общего адресного пространства Alpha.AccessPoint, механизм привязки статических
сигналов имеет приоритет перед механизмом привязки ветвей.
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА
25

=== Page 178 ===
3. НАСТРОЙКА
3.7. Передача данных через файловый интерфейс
Файловый интерфейс представляет собой безопасный метод передачи данных при обмене информацией
между защищенными подсетями. В данном режиме TCP Server Module (в составе источника данных)
циклически генерирует DAT-файлы, содержащие значения сигналов. HUB Module (в составе
Alpha.AccessPoint) периодически считывает значения сигналов из DAT-файла.
Генерация DAT-файлов модулем TCP Server
Чтобы TCP Server Module генерировал DAT-файлы, перейдите в ветку модуля Настройка файлового
интерфейса и добавьте новый файл. Укажите ветвь дерева сигналов, значения которых будут циклически
записываться в DAT-файл (параметр Папка дерева сигналов).
В параметре Полное имя папки для сохранения данных укажите путь к папке, в которую TCP Server Module
будет генерировать DAT-файлы.
ОБРАТИТЕ ВНИМАНИЕ
Если DAT-файлы предполагается генерировать в папку другого сетевого компьютера (например по
сетевому пути: \\NetworkComputer\SharedFolder\), то для этой папки должна быть разрешена
запись серверу, в составе которого работает TCP Server Module. Доступ на запись настраивается
стандартными способами операционной системы.
Прочие параметры генерации файлов:
Период генерации файлов,
мсек
Задаёт периодичность обновления информации в DAT-файлах
Максимальное количество
изменений в файле
Устанавливает лимит числа изменений. Если лимит будет превышен, то
будет создан дополнительный файл
Период записи всех
данных, сек
Период принудительного обновления данных по всем сигналам (вне
зависимости от того, изменились ли значения сигналов)
26
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 179 ===
3. НАСТРОЙКА
Чтобы вручную принудительно обновить данные по всем сигналам в файле, подайте команду «TRUE» в
служебный сигнал с тегом:
Service.Modules.TCP Server Module.Sources.<имя файла>.WriteAllData.Command
На рисунке ниже показан сгенерированный DAT-файл. В его имени присутствует уникальный идентификатор
конфигурации источника данных.
Чтение DAT-файлов модулем HUB Module
Группа параметров Настройки файлового интерфейса (ветвь Источники в параметрах HUB Module) отвечает
за чтение DAT-файлов.
Включить
интерфейс
Параметр активирует режим файлового интерфейса
ВАЖНО
Если для Источника активирован режим файлового интерфейса, то настройки
серверов и каналов будут игнорироваться
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА
27

=== Page 180 ===
3. НАСТРОЙКА
Полное
имя папки
для
чтения
данных
Путь до папки, где хранится файл со значениями сигналов
ОБРАТИТЕ ВНИМАНИЕ
Если DAT-файлы предполагается читать из папки другого сетевого компьютера
(например по сетевому пути: \\NetworkComputer\SharedFolder\), то для этой папки
должно быть разрешено чтение серверу, в составе которого работает HUB Module.
Доступ на чтение настраивается стандартными способами операционной системы.
Таймаут
потери
связи,
мсек
После истечения таймаута сигналам, передаваемым через файловый интерфейс,
выставляется качество COMM_FAILURE (24)
Данные, считанные из DAT-файлов, попадают в значения статических сигналов, которые должны быть
подготовлены заранее.
3.8. Защита от несанкционированного доступа
Установка пароля для доступа к Alpha.AccessPoint дает следующие возможности:
предотвращает несанкционированный доступ к модификации конфигурации из сервисного
приложения Конфигуратор;
предотвращает несанкционированный доступ к просмотру статистики из сервисного приложения
Статистика.
Все операции с паролем (создание/изменение) выполняются в окне Смена пароля, которое запускается
командой меню Сервер →Сменить пароль сервера из сервисного приложении Конфигуратор.
ОБРАТИТЕ ВНИМАНИЕ
После первого подключения к серверу (не требует ввода пароля) следует назначить пароль через
окно Смена пароля.
28
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 181 ===
4. ПОЛУЧЕНИЕ ДАННЫХ ОТ ALPHA.ACCESSPOINT
4. Получение данных от Alpha.AccessPoint
4.1. Получение оперативных значений сигналов по OPC
DA
ОБРАТИТЕ ВНИМАНИЕ
Спецификация OPC DA базируются на COM/DCOM и используются только в ОС Windows.
После того, как Alpha.AccessPoint был сконфигурирован, подключитесь к нему любым OPC DA клиентом.
Стандартный ProgID для подключения: «AP.OPCDAServer.AccessPoint». После подключения вы можете
работать с сигналами объединенного дерева, а также со следующими свойствами сигналов:
1 (CDT);
101 (DESCRIPTION);
100 (EUNIT);
5 (ACCRIGHT);
9001;
5100 (RECALC_RAW_LOW);
5101 (RECALC_RAW_MIDDLE);
5102 (RECALC_RAW_HIGH);
5103 (RECALC_VAL_LOW);
5104 (RECALC_VAL_MIDDLE);
5105 (RECALC_VAL_HIGH);
5106 (RECALC_TRUNCATE);
5107(RECALC_SET_FAILURE_QUALITY);
5108 (RECALC_INVERT);
999000 (ObjectType).
4.2. Получение оперативных событий по OPC AE
ОБРАТИТЕ ВНИМАНИЕ
Спецификация OPC AE базируются на COM/DCOM и используются только в ОС Windows.
Alpha.AccessPoint может выступать в качестве единой точки приема событий технологического процесса,
генерируемых на подключенных источниках данных. Для этого добавьте в состав конфигурации
Alpha.AccessPoint модуль OPC AE Server и активируйте его.
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА
29

=== Page 182 ===
4. ПОЛУЧЕНИЕ ДАННЫХ ОТ ALPHA.ACCESSPOINT
После этого вы сможете отслеживать события всех источников данных, подключившись к
Alpha.AccessPoint любым OPC AE-клиентом (например, через приложение Alpha.Alarms). Стандартный
ProgID для подключения: «AP.OPCAEServer.AccessPoint».
Квитирование событий
Когда пользователь квитирует событие в подключённом к Alpha.AccessPoint клиенте, Alpha.AccessPoint
передаёт информацию о квитировании события в источник данных, в котором оно произошло.
Если источником данных является пара серверов, работающих в режиме дублирования или в режиме
горячего резервирования, то информация о квитировании передаётся в оба сервера.
4.3. Получение оперативных данных по OPC UA
OPC UA является унифицированной спецификацией, объединяющей в себе возможности спецификаций
OPC DA и OPC AE. Чтобы получить доступ к оперативным значениям сигналов и событиям
Alpha.AccessPoint по спецификации OPC UA, добавьте в конфигурацию модуль OPC UA и произведите его
настройку.
30
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 183 ===
4. ПОЛУЧЕНИЕ ДАННЫХ ОТ ALPHA.ACCESSPOINT
После настройки модуля OPC UA возможно подключение к Alpha.AccessPoint любым OPC UA клиентом.
Получение оперативных значений сигналов
Чтобы получать оперативные значения сигналов, выполните следующие действия:
1. Создайте в дереве проекта элемент типа Documents - Data Access View.
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА
31

=== Page 184 ===
4. ПОЛУЧЕНИЕ ДАННЫХ ОТ ALPHA.ACCESSPOINT
2. Перетащите сигналы, значения которых вы хотите получать, из адресного пространства сервера на
вкладку Data Access View. Значения добавленных сигналов будут обновляться автоматически.
Получение оперативных событий
Чтобы получать оперативные события, выполните следующие действия:
1. Создайте в дереве проекта элемент типа Documents - Event View.
32
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 185 ===
4. ПОЛУЧЕНИЕ ДАННЫХ ОТ ALPHA.ACCESSPOINT
2. Перетащите из адресного пространства сервера на вкладку Event View сигналы, события по которым
вы хотите получать.
Чтобы получать все события, происходящие на сервере, перетащите элемент Server из адресного
пространства сервера на вкладку Event View.
4.4. Получение исторических данных по OPC UA
Alpha.AccessPoint можно настроить на запрос истории значений сигналов из БД и предоставление
исторических данных по спецификации OPC UA. Для выполнения этой задачи конфигурация
Alpha.AccessPoint должна включать модули:
History Module (далее - модуль истории) - работает в режиме чтения и выполняет выборку истории из
хранилища по определенным id сигналов;
OPC UA - предоставляет исторические данные клиентам по спецификации OPC UA.
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА
33

=== Page 186 ===
4. ПОЛУЧЕНИЕ ДАННЫХ ОТ ALPHA.ACCESSPOINT
ОБРАТИТЕ ВНИМАНИЕ
Конфигурация источника должна включать модуль TCP Server Module - для предоставления ID
сигналов, по которым требуется выборка истории.
В узле Источники модуля HUB Module необходимо создать источник данных. В узле источника данных
настройте параметры привязки Папка источник и Папка приемник (стр. 22). Привязка должна загружать в
Alpha.AccessPoint все узлы источника, по которым имеются исторические данные.
После произведенных настроек подключитесь к Alpha.AccessPoint любым OPC UA клиентом (в примере
ниже показан клиент UA Expert) и запросите историю изменений значений сигналов.
34
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 187 ===
4. ПОЛУЧЕНИЕ ДАННЫХ ОТ ALPHA.ACCESSPOINT
Для работы с историческими данными создайте в дереве проекта элемент типа Documents - History Trend
View.
Для работы с историческими данными перетаскивайте необходимые сигналы из дерева Alpha.AccessPoint
на вкладку History Trend View. В области Single Update задайте начальное и конечное время для
построения графика истории и нажмите Update.
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА
35

=== Page 188 ===
4. ПОЛУЧЕНИЕ ДАННЫХ ОТ ALPHA.ACCESSPOINT
Чтобы просмотреть информацию по истории изменений добавленного сигнала в табличной форме, перейдите
на соседнюю вкладку с именем добавленного сигнала.
36
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 189 ===
5. ПРИМЕР НАСТРОЙКИ
5. Пример настройки
Есть 2 источника данных. Каждый источник данных состоит из пары серверов (резервная пара в режиме
горячего резервирования). У каждого сервера есть 2 канала связи. Каналы связи работают по разным
физическим линиям передачи данных и настроены на разные IP-адреса. Сетевые адреса и порты каналов
показаны на схеме ниже.
Требуется настроить Alpha.AccessPoint для работы с двумя источниками данных и настроить привязки так,
чтобы дерево общего адресного пространства имело структуру, как на схеме ниже.
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА
37

=== Page 190 ===
5. ПРИМЕР НАСТРОЙКИ
Деревья источников должны обновляться в Alpha.AccessPoint с паузой в 20 секунд, а период отправки
пакетов от источников (по 100 сигналов в каждом пакете) не должен превышать 1 секунду.
Обязательные условия для успешного подключения Alpha.AccessPoint к Alpha.Server:
наличие на всех Alpha.Server, модулей TCP Server Module в состоянии активности;
для каждого канала должен быть задан уникальный IP-адрес.
Ниже описаны шаги по настройке HUB Module в составе Alpha.AccessPoint для решения поставленной
задачи:
создать 2 источника данных (стр. 16):
Источник 1:
Пауза между процедурами по обновлению дерева, сек - 20;
Максимальное количество сигналов в пакете – 100;
Период отправки пакетов – 1000;
Обновлять всегда – да.
Источник 2:
Параметры аналогичны Источнику 1.
к каждому источнику данных создать по одной привязке (стр. 22):
Привязка источника 1:
папка приемник: AK.DMN.R_Bel;
папка источник: AK.DMN.R_Bel.
Привязка источника 2:
папка приемник: AK.DMN.R_Dal;
папка источник: AK.DMN.R_Dal.
для каждого источника создать по 2 сервера (стр. 19):
основной сервер;
резервный сервер.
в составе каждого сервера завести по 2 канала (стр. 20):
основной канал;
резервный канал.
38
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 191 ===
5. ПРИМЕР НАСТРОЙКИ
для всех созданных каналов сконфигурировать параметры подключения (схема выше):
IP-адрес;
порт.
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА
39

=== Page 192 ===
6. ДИАГНОСТИКА РАБОТЫ
6. Диагностика работы
Для диагностики работы Alpha.AccessPoint и его модулей воспользуйтесь сервисными приложениями
Статистика и сервисным приложением Просмотрщик лога кадров.
ОБРАТИТЕ ВНИМАНИЕ
Сервисные приложения могут быть установлены только на компьютере под управлением ОС
Windows.
Статистика:
Просмотрщик лога кадров:
Для мониторинга состояния связи с серверами источника по разным каналам в Alpha.AccessPoint
используются сервисные сигналы в папке:
40
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 193 ===
6. ДИАГНОСТИКА РАБОТЫ
Service.Modules.HUB Module.Source N.Server N.Channels.ChannelN
Тег сигнала
Тип
Описание
«Active»
bool
Активность канала
«ConnectionState»
bool
Состояние связи по каналу
«IP_Address»
string
IP-адрес канала
«Port»
uint2
Порт канала
Для мониторинга состояния файлового интерфейса используются сервисные сигналы в папке:
Service.Modules.HUB Module.Sources.Источник N
Тег сигнала
Тип
Описание
«ConnectionState»
bool
Состояние связи с источником
«ExchangeFolder»
string
Путь к папке обмена файлами
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА
41

=== Page 194 ===
СПИСОК ТЕРМИНОВ И СОКРАЩЕНИЙ
Список терминов и сокращений
IP (Internet Protocol)
Протокол IP, межсетевой протокол, протокол межсетевого
взаимодействия – базовый интернет-протокол.
OPC (OLE for Process
Control)
Программная технология на базе OLE, ActiveX, COM/DCOM,
предоставляющая набор объектов, используемых в автоматизации
технологических процессов, и интерфейсов доступа к ним.
OPC AE (OLE for Process
Control Alarms and
Events)
Спецификация, которая описывает набор интерфейсов, предоставляющих
функции уведомления о событиях технологических процессов.
OPC DA (OLE for Process
Control Data Access)
Интерфейс передачи сигналов OPC, описывает набор функций обмена
данными в реальном времени.
OPC UA (OPC Unified
Architecture)
Унифицированная спецификация, определяющая передачу данных в
промышленных сетях.
OPC сервер
Сервер, предоставляющий доступ по интерфейсам OPC к
технологическим данным, полученным по различным каналам, главным
образом, от среднего уровня АСУ ТП. Обычно разрабатывается
производителем контроллеров, автоматики.
TCP (Transmission
Control Protocol)
Протокол управления передачей.
TCP/IP
Стек сетевых протоколов передачи данных.
Качество сигнала
Характеристика достоверности сигнала.
ОС
Операционная система.
Сигнал
Единица технологической информации, обладающая определённым
набором обязательных и дополнительных свойств.
42
ALPHA.ACCESSPOINT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 195 ===
Программный комплекс Альфа платформа
Alpha.Imitator 6.4
Руководство администратора
Редакция
Соответствует версии ПО
7. Предварительная
6.4.28

=== Page 196 ===
© АО «Атомик Софт», 2015-2026. Все права защищены.
Авторские права на данный документ принадлежат АО «Атомик
Софт». Копирование, перепечатка и публикация любой части или
всего документа не допускается без письменного разрешения
правообладателя.

=== Page 197 ===
Содержание
1. Назначение и принцип работы
5
1.1. Воспроизведение истории
5
1.2. Перезапись исторических данных
5
1.3. Дополнение пропущенных исторических данных
6
2. Подготовка к работе
7
2.1. Установка Alpha.Imitator
7
2.1.1. ОС Windows
7
2.1.2. ОС Linux
7
2.2. Запуск и останов Alpha.Imitator
8
2.2.1. ОС Windows
8
2.2.2. ОС Linux
8
2.3. Удаление Alpha.Imitator
8
2.3.1. ОС Windows
8
2.3.2. ОС Linux
8
3. Настройка Alpha.Imitator в Alpha.DevStudio
10
3.1. Добавление Alpha.Imitator в проект
10
3.2. Настройки БД
11
3.2.1. Добавление БД в Alpha.Historian
12
3.2.2. Сохранение истории в БД
12
3.3. Настройка источника данных
13
3.4. Настройка приложения Alpha.Server и Alpha.Imitator
15
3.5. Настройка логических типов
16
3.6. Настройки для режима воспроизведения истории
18
3.6.1. Настройка БД для воспроизведения истории
18
3.6.2. Настройка сигналов для воспроизведения истории
19
3.6.3. Требуемые модули Alpha.Imitator
20
3.7. Настройки для режима перезаписи истории
20
3.7.1. Настройка БД для перезаписи истории
20
3.7.2. Настройка сигналов для перезаписи истории
21
3.7.3. Требуемые модули Alpha.Imitator
23
3.8. Настройки для режима дополнения истории
23
3.8.1. Настройка БД для дополнения истории
23
3.8.2. Настройка сигналов для дополнения истории
24
3.8.3. Настройка передачи данных через файловый интерфейс
24
3.9. Применение конфигураций Alpha.Server и Alpha.Imitator
27
4. Настройка Alpha.Imitator в Конфигураторе
29
4.1. Настройка конфигурации для режима воспроизведения истории
29
4.1.1. Настройка сигналов
29
4.1.2. Требуемые модули
29
4.1.3. Настройка сохранения данных в имитационную БД
30
4.2. Настройка конфигурации для режима перезаписи истории
30
4.2.1. Настройка сигналов
31
4.2.2. Требуемые модули
31
4.2.3. Настройка сохранения данных в БД
32
4.3. Настройка конфигурации для режима дополнения истории
32
4.3.1. Настройка сигналов
33
4.3.2. Требуемые модули
33
4.3.3. Настройка сохранения данных в БД
33
4.3.4. Настройка файлового интерфейса
34
4.4. Сохранение конфигурации Alpha.Server
34
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
3

=== Page 198 ===
4.5. Загрузка конфигурации в Alpha.Imitator
35
5. Служебные сигналы Alpha.Imitator
36
6. Работа с Alpha.Imitator
40
6.1. Воспроизведение истории
40
6.2. Перезапись исторических данных
43
6.2.1. Перезапись единственного значения
44
6.2.2. Перезапись массива данных
48
6.3. Дополнение пропущенных исторических данных
55
7. Приложения
56
Приложение A: Создание имитационной базы данных
56
Приложение B: Формат datetime_json
57
Приложение C: Формат trend_json
58
4
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 199 ===
1. НАЗНАЧЕНИЕ И ПРИНЦИП РАБОТЫ
1. Назначение и принцип работы
Alpha.Imitator – компонент Альфа платформы, предназначенный для выполнения следующих функций:
воспроизведения истории технологического процесса;
перезаписи исторических данных;
дополнения пропущенных исторических данных.
Общая схема системы с Alpha.Imitator приведена ниже.
Alpha.Server получает данные от нижестоящих систем и выполняет логическую обработку полученных
данных. Затем Alpha.Server записывает вычисленные значения в Alpha.Historian. Alpha.Imitator в
зависимости от режима работы:
воспроизводит историю изменения значений сигналов и передаёт клиенту;
пересчитывает значения и перезаписывает скорректированные данные в Alpha.Historian;
записывает пропущенные данные в Alpha.Historian.
Для выполнения каждой из перечисленных функций Alpha.Imitator нужно запустить в соответствующем
режиме работы.
1.1. Воспроизведение истории
Alpha.Imitator позволяет загружать исторические данные из Alpha.Historian за указанный интервал времени
и проигрывать исторические данные в виде потока оперативных данных. Воспроизведение истории позволяет
пользователю просмотреть историю хода технологического процесса на графиках или мнемосхемах.
Для режима воспроизведения истории необходима отдельная база для имитационных данных.
1.2. Перезапись исторических данных
Alpha.Imitator позволяет выполнять пересчёт значений на основе параметров, значения которых задаёт
пользователь, и записывать пересчитанные значения в Alpha.Historian за определенный промежуток
времени вместо уже имеющихся исторических данных с теми же метками времени.
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
5

=== Page 200 ===
1. НАЗНАЧЕНИЕ И ПРИНЦИП РАБОТЫ
Alpha.Imitator может перезаписывать как единственное значение, так и массив данных.
Перезапись единственного значения используется в случае, если требуется перезаписать значение тега, на
основе которого будут пересчитаны зависимые параметры. При этом единственное заданное значение тега
будут действовать на всём интервале имитации.
Перезапись массива данных используется в случае, если требуется перезаписать несколько значений тега,
на основе которых будут пересчитаны зависимые параметры. При этом каждое из заданных значений будет
действовать в соответствующем промежутке интервала имитации.
1.3. Дополнение пропущенных исторических данных
Если через файловый интерфейс Alpha.Server не удаётся получить все файлы данных (например, из-за
некорректной передачи файлов по сети), то в Alpha.Historian в определенные промежутки времени
исторические данные будут отсутствовать.
Alpha.Imitator позволяет записывать отсутствующие данные в Alpha.Historian. Для этого следует поместить
непереданные файлы данных в заданную папку и запустить Alpha.Imitator в режиме дополнения
пропущенных данных. На основе данных, содержащихся в файлах, Alpha.Imitator пересчитывает значения и
записывает в соответствующие временные промежутки в Alpha.Historian.
6
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 201 ===
2. ПОДГОТОВКА К РАБОТЕ
2. Подготовка к работе
Alpha.Imitator функционирует в виде:
службы Alpha.Imitator в ОС Windows;
сервиса alpha.imitator в ОС Linux.
2.1. Установка Alpha.Imitator
2.1.1. ОС Windows
Для установки Alpha.Imitator запустите установочный файл Alpha.Imitator-x.x.x xxxxxx (x64).msi и
следуйте инструкциям мастера установки.
Установка выполняется в папку: C:\Program Files\Automiq\Alpha.Imitator.
2.1.2. ОС Linux
ОБРАТИТЕ ВНИМАНИЕ
Команда установки выполняется только от суперпользователя «root».
Имя устанавливаемого пакета: alpha.imitator-x.x.x+xx.xxxxx.deb или alpha.imitator-
x.x.x+xx.xxxxx.rpm в зависимости от используемой ОС Linux. Находясь в папке с установочным пакетом,
запустите установку.
Установка пакета *.rpm с помощью пакетного менеджера YUM:
yum install alpha.imitator-x.x.x+xx.xxxxx.rpm
Установка пакета *.rpm с помощью пакетного менеджера RPM:
rpm -i alpha.imitator-x.x.x+xx.xxxxx.rpm
Установка пакета *.deb с помощью пакетного менеджера apt:
apt-get install alpha.imitator-x.x.x+xx.xxxxx.deb
Установка пакета *.deb с помощью пакетного менеджера dpkg:
sudo dpkg -i alpha.imitator-x.x.x+xx.xxxxx.deb
Alpha.Imitator устанавливается в директорию /opt/Automiq/Alpha.Imitator.
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
7

=== Page 202 ===
2. ПОДГОТОВКА К РАБОТЕ
2.2. Запуск и останов Alpha.Imitator
2.2.1. ОС Windows
Управление Alpha.Imitator выполняется путем запуска/перезапуска/останова службы Alpha.Imitator
стандартными инструментами ОС Windows.
2.2.2. ОС Linux
Управление Alpha.Imitator выполняется путем запуска/перезапуска/останова сервиса alpha.imitator
специализированными командами.
ОБРАТИТЕ ВНИМАНИЕ
Все команды выполняются только от суперпользователя «root».
Запуск:
systemctl start alpha.imitator
Останов:
systemctl stop alpha.imitator
Перезапуск:
systemctl restart alpha.imitator
2.3. Удаление Alpha.Imitator
2.3.1. ОС Windows
Удаление Alpha.Imitator выполняется стандартными инструментами ОС Windows:
1. Запустите Программы и компоненты: Пуск →Панель управления →Программы и компоненты.
2. Из представленного списка установленных программ выберете Alpha.Imitator и нажмите кнопку
Удалить.
2.3.2. ОС Linux
Удаление Alpha.Imitator выполняется штатным пакетным менеджером.
ОБРАТИТЕ ВНИМАНИЕ
Команда удаления выполняется только от суперпользователя «root».
Удаление пакета *.rpm с помощью пакетного менеджера YUM:
8
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 203 ===
2. ПОДГОТОВКА К РАБОТЕ
yum remove alpha.imitator
Удаление пакета *.rpm с помощью пакетного менеджера RPM:
rpm -e alpha.imitator
Удаление пакета *.deb с помощью пакетного менеджера apt:
apt-get remove alpha.imitator
Удаление пакета *.deb с помощью пакетного менеджера dpkg:
dpkg -r alpha.imitator
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
9

=== Page 204 ===
3. НАСТРОЙКА ALPHA.IMITATOR В ALPHA.DEVSTUDIO
3. Настройка Alpha.Imitator в Alpha.DevStudio
Чтобы настроить Alpha.Imitator:
в проект добавьте Alpha.Imitator и выполните настройку Alpha.Domain (стр. 10);
выполните настройки БД: настройте сохранение исторических данных Alpha.Server в БД
Alpha.Historian (стр. 11);
настройте источник данных для Alpha.Server (стр. 13);
настройте приложение для Alpha.Server и Alpha.Imitator (стр. 15);
выполните настройки, необходимые для требуемого режима работы Alpha.Imitator;
примените конфигурации Alpha.Server и Alpha.Imitator (стр. 27).
ОБРАТИТЕ ВНИМАНИЕ
Порядок создания проекта и конфигурирование Alpha.Server и Alpha.Historian описаны в
документации на Alpha.DevStudio (Руководство пользователя: разделы «Знакомство с
Alpha.DevStudio. Создание простого проекта» и «Разработка проекта. Сохранение значений и
событий»).
Далее приведено описание настройки воспроизведения истории в существующем проекте, в котором
уже сконфигурирован Узел Alpha.Domain «host», содержащий Alpha.Server и Alpha.Historian.
3.1. Добавление Alpha.Imitator в проект
1. Перейдите в Узел Alpha.Domain «host» и добавьте элемент Alpha.Imitator.
2. В файле конфигурации alpha.domain.agent.xml (расположен в папке C:\Program
Files\Automiq\Alpha.Domain) выполните следующие настройки:
10
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 205 ===
3. НАСТРОЙКА ALPHA.IMITATOR В ALPHA.DEVSTUDIO
2.1. В элемент InstalledComponents добавьте дочерний элемент Alpha.Server с атрибутами:
Name – произвольное имя;
ServiceName – имя службы Alpha.Imitator .
<?xml version="1.0" encoding="utf-8"?>
<Alpha.Domain.Agent Name="NDA">
<EntryPointNetAgent Name="ARM" Address="127.0.0.1" Port="1010"/>
<InstalledComponents>
<Alpha.Server Name="Server" ServiceName="Alpha.Server"/>
<Alpha.Server Name="Imitator" ServiceName="Alpha.Imitator"/>
</InstalledComponents>
<Server>
<Components StoragePath="c:\DomainStorage\cache\server">
<Component InstalledName="Server" Name="Server" StorageLimitSize="0"
StorageLimitNum="0"/>
</Components>
</Server>
<Options LoggerLevel="2"/>
</Alpha.Domain.Agent>
2.2. В элементе Server для дочернего элемента Components добавьте элемент Component с
атрибутами:
InstalledName – значение атрибута Name элемента InstalledComponents, добавленного на
предыдущем шаге;
Name – имя Alpha.Imitator, используемое в Alpha.DevStudio.
<?xml version="1.0" encoding="utf-8"?>
<Alpha.Domain.Agent Name="NDA">
<EntryPointNetAgent Name="ARM" Address="127.0.0.1" Port="1010"/>
<InstalledComponents>
<Alpha.Server Name="Server" ServiceName="Alpha.Server"
DefaultActivation="1"/>
<Alpha.Server Name="Imitator" ServiceName="Alpha.Imitator"
DefaultActivation="1"/>
</InstalledComponents>
<Server>
<Components StoragePath="c:\DomainStorage\cache\server">
<Component InstalledName="Server" Name="Server" StorageLimitSize="0"
StorageLimitNum="0"/>
<Component InstalledName="Imitator" Name="Imitator"
StorageLimitSize="0" StorageLimitNum="0"/>
</Components>
</Server>
<Options LoggerLevel="2"/>
</Alpha.Domain.Agent>
3.2. Настройки БД
В Alpha.Historian добавьте и настройте БД.
В Alpha.Server укажите БД, в которые будут сохраняться значения.
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
11

=== Page 206 ===
3. НАСТРОЙКА ALPHA.IMITATOR В ALPHA.DEVSTUDIO
3.2.1. Добавление БД в Alpha.Historian
1. Перейдите в Узел Alpha.Domain «host» и на элементе Alpha.Historian нажмите кнопку
для
добавления баз данных.
2. Добавьте две базы данных:
для имитационных данных (будет использоваться в режиме воспроизведения истории);
для сохранения значений (будет использоваться в режимах перезаписи и дополнения истории).
3. Для первой базы данных укажите значения свойств:
Псевдоним - имя имитационной базы данных, указанной в настройкахAlpha.Historian: «imitdb1»
(стр. 56);
Тип использования - «Имитационные данные».
Значение параметра Имя можно указать произвольное.
4. Для второй базы данных укажите значения свойств:
Псевдоним - имя базы данных, указанной в настройках Alpha.Historian: «default» (стр. 56);
Тип использования - «Для значений».
Значение параметра Имя можно указать произвольное.
3.2.2. Сохранение истории в БД
1. Перейдите в Alpha.Server и на элементе Модуль истории нажмите кнопку
для добавления баз
данных, в которые будет записываться история.
2. Добавьте две базы данных:
для имитационных данных;
для сохранения значений.
12
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 207 ===
3. НАСТРОЙКА ALPHA.IMITATOR В ALPHA.DEVSTUDIO
3. Для имитационной БД укажите значения свойств:
Короткое имя БД очереди - имя имитационной базы данных, в которую будет записываться
история - «imitdb1»;
Режим работы с хранилищем - «Чтение и запись».
4. Для БД сохранения значений укажите значения свойств:
Короткое имя БД очереди - имя базы данных, в которую будет записываться история -
«default»;
Режим работы с хранилищем - «Чтение и запись».
3.3. Настройка источника данных
Настройте источник, от которого Alpha.Server будет получать данные. Источником данных может быть ПЛК
или сервер. Далее приведена настройка источника, которым является другой Alpha.Server. Обмен данными
между Alpha.Server и источникам будет выполняться по TCP:
1. Перейдите в Alpha.Domain и добавьте элемент Узел Alpha.Domain. Задайте имя, например, «Source».
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
13

=== Page 208 ===
3. НАСТРОЙКА ALPHA.IMITATOR В ALPHA.DEVSTUDIO
2. Перейдите в Узел Alpha.Domain «Source», укажите адрес Адаптера Ethernet и добавьте элемент
Alpha.Server.
3. Перейдите в Alpha.Server и добавьте элемент Приложение. В дальнейшем в это приложение будут
добавлены логические типы источника.
4. Вернитесь в Alpha.Domain и соедините Адаптер Ethernet добавленного источника с Сетью Ethernet.
5. Перейдите в Узел Alpha.Domain «host», содержащий Alpha.Server, Alpha.Historian и Alpha.Imitator.
6. Перейдите в Alpha.Server и добавьте HUB Module.
14
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 209 ===
3. НАСТРОЙКА ALPHA.IMITATOR В ALPHA.DEVSTUDIO
7. Для HUB Module укажите ранее настроенный источник данных.
3.4. Настройка приложения Alpha.Server и Alpha.Imitator
Конфигурации Alpha.Server и Alpha.Imitator должны быть одинаковыми. Поэтому Приложение,
описывающее набор параметров, должно быть общее для Alpha.Server и Alpha.Imitator. Для этого следует
разместить Приложение в Alpha.Domain, а из Alpha.Server и Alpha.Imitator сослаться на данное Приложение:
1. Перейдите в Alpha.Domain и добавьте элемент Приложение. В дальнейшем в это приложение будут
добавлены логические типы Alpha.Server.
2. Перейдите в Узел Alpha.Domain «host», а затем в Alpha.Server.
3. Добавьте в Alpha.Server элемент Исполняемый модуль приложения.
4. В свойстве Исполняемые объекты добавленного элемента укажите добавленное ранее Приложение.
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
15

=== Page 210 ===
3. НАСТРОЙКА ALPHA.IMITATOR В ALPHA.DEVSTUDIO
5. Перейдите в Alpha.Imitator и выполните те же действия: добавьте элемент Исполняемый модуль
приложения и укажите Приложение.
3.5. Настройка логических типов
Для настройки обмена данными между источником и Alpha.Server необходимо настроить соответствующие
логические типы.
1. Добавьте в проект элемент Пространство имен и задайте Имя, например, «Types». Перейдите в
пространство имён «Types» и добавьте ещё два элемента Пространство имен. Каждому элементу
задайте Имя, например, «SourceType» и «ServerType». Это будут папки с логическими типами источника и
Alpha.Server.
16
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 211 ===
3. НАСТРОЙКА ALPHA.IMITATOR В ALPHA.DEVSTUDIO
2. В каждое Пространство имен добавьте элемент Аспект.
Задайте Имя каждому добавленному аспекту:
в пространстве имён «SourceType» - аспект «Source»;
в пространстве имён «ServerType» - аспект «Server».
Логический тип источника
1. Перейдите в Пространство имен «SourceType» и добавьте элемент Логический тип. В свойствах
добавленного логического типа укажите:
Имя - имя логического типа источника;
Аспект - добавленный ранее аспект «Source».
2. Перейдите в добавленный Логический тип и опишите его структуру: добавьте сигналы необходимых
типов, укажите им Имя и требуемое Направление.
Логический тип Alpha.Server
1. Перейдите в Пространство имен «ServerType» и добавьте элемент Логический тип. В свойствах
добавленного логического типа укажите:
Имя - имя логического типа Alpha.Server;
Аспект - добавленный ранее аспект «Server»;
Представляемый тип - описанный ранее логический тип источника.
Добавленный Логический тип будет представлять описанный ранее логический тип источника, только со
стороны Alpha.Server.
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
17

=== Page 212 ===
3. НАСТРОЙКА ALPHA.IMITATOR В ALPHA.DEVSTUDIO
2. Перейдите в добавленный Логический тип и добавьте элемент Ссылка. В свойствах добавленной
ссылки укажите:
Имя - имя ссылки;
Тип - описанный ранее логический тип источника.
После указания Типа в элементе Ссылка отобразится структура логического типа ПЛК. Добавленная
ссылка будет связывать логический тип Alpha.Server с логическим типом ПЛК.
3. В контекстном меню ссылки выполните команду Экспонировать входы и выходы, в результате чего в
логическом типе Alpha.Server будут созданы сигналы с теми же именами и типами, что и в логическом
типе ПЛК, а также прорисованы связи.
3.6. Настройки для режима воспроизведения истории
Для работы Alpha.Imitator в режиме воспроизведения истории выполните следующие настройки:
настройте БД, из которой будет воспроизводиться история;
настройте сигналы, для которых требуется воспроизводить историю;
в конфигурацию Alpha.Imitator добавьте требуемые модули.
3.6.1. Настройка БД для воспроизведения истории
1. В Узле Alpha.Domain «host» перейдите в Alpha.Imitator и на элементе Модуль истории нажмите кнопку
для добавления имитационной базы данных Alpha.Historian, из которой будут загружаться
исторические данные для дальнейшего воспроизведения истории.
2. Для добавленной имитационной БД укажите значения свойств:
Короткое имя БД очереди - имя имитационной базы данных, из которой будет читаться история
для воспроизведения - «imitdb1»;
Режим работы с хранилищем - «Чтение и запись».
18
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 213 ===
3. НАСТРОЙКА ALPHA.IMITATOR В ALPHA.DEVSTUDIO
3.6.2. Настройка сигналов для воспроизведения истории
Например, пусть требуется воспроизводить историю изменения значений сигнала «Process.Parameter». Для
этого выполните следующие настройки:
1. Перейдите в Пространство имен «SourceType» и добавьте Логический тип источника - «Process» (стр.
17).
2. Перейдите в добавленный тип «Process» и опишите его структуру (стр. 17). Данный логический тип
имеет один выходной параметр типа Uint4.
3. Перейдите в Пространство имен «ServerType» и добавьте Логический тип для представления
логического типа источника, только со стороны Alpha.Server. Например, «Process».
4. Перейдите в добавленный логический тип «Process» и свяжите его с логическим типом «Process»
источника.
5. Для появившегося сигнала «Parameter» настройте сохранение истории. Для этого выделите сигнал
«Parameter» и на вкладке История установите флаг Сохранять историю.
6. Перейдите в источник «Source», а затем в приложение источника «Application», и добавьте
экземпляр логического типа источника «Process».
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
19

=== Page 214 ===
3. НАСТРОЙКА ALPHA.IMITATOR В ALPHA.DEVSTUDIO
7. Перейдите в Узел Alpha.Domain «host», а затем в приложение «Application», и добавьте экземпляр
логического типа Alpha.Server «Process».
Добавленному типу на вкладке Свойства укажите Представляемый объект - экземпляр логического типа
источника «Process», ранее добавленный в приложение источника.
8. Инициализируйте ссылку:
вызовите контекстное меню и выполните команду Инициализировать все ссылки;
нажмите кнопку
на панели инструментов или клавишу «F5» на клавиатуре.
3.6.3. Требуемые модули Alpha.Imitator
1. Перейдите в Узел Alpha.Domain «host», а затем в Alpha.Imitator.
2. Чтобы Alpha.Imitator предоставлял имитационные данные по TCP клиенту, например
Alpha.HMI.Trends, добавьте модуль TCP Server.
3.7. Настройки для режима перезаписи истории
Для работы Alpha.Imitator в режиме перезаписи истории выполните следующие настройки:
настройте БД, в которой будет перезаписываться история;
настройте сигналы, для которых требуется перезаписывать историю;
в конфигурацию Alpha.Imitator добавьте требуемые модули.
3.7.1. Настройка БД для перезаписи истории
1. В Узле Alpha.Domain «host» перейдите в Alpha.Imitator и на элементе Модуль истории нажмите кнопку
для добавления базы данных, в которую будут перезаписываться исторические данные.
20
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 215 ===
3. НАСТРОЙКА ALPHA.IMITATOR В ALPHA.DEVSTUDIO
2. Для добавленной базы данных укажите значения свойств:
Короткое имя БД очереди - имя базы данных, в которую будет перезаписываться история -
«default»;
Режим работы с хранилищем - «Чтение и запись».
3.7.2. Настройка сигналов для перезаписи истории
Например, пусть значение сигнала «ASRMB.Item» вычисляется на основе значения сигнала «ASRMB.Recalc» по
формуле:
ASRMB.Item = ASRMB.Recalc + 10
Требуется пересчитать и перезаписать в Alpha.Historian значения сигнала «ASRMB.Item» на основе новых
значений сигнала «ASRMB.Recalc». Для этого выполните следующие настройки:
1. Перейдите в Пространство имен «SourceType» и добавьте Логический тип источника «ASRMB» (стр. 17).
2. Перейдите в добавленный тип «ASRMB» и опишите его структуру (стр. 17). Данный логический тип имеет
один выходной параметр типа Int4.
3. Перейдите в Пространство имен «ServerType» и добавьте Логический тип для представления
логического типа источника, только со стороны Alpha.Server. Например, «ASRMB».
4. Перейдите в добавленный логический тип «ASRMB» и свяжите его с логическим типом «ASRMB»
источника.
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
21

=== Page 216 ===
3. НАСТРОЙКА ALPHA.IMITATOR В ALPHA.DEVSTUDIO
5. В логический тип «ASRMB» добавьте параметр «Item» типа Int4 и на вкладке Формулы укажите формулу
для рассчёта значения.
6. Для параметров «Item» и «Recalc» настройте сохранение истории. Для этого выделите параметры и на
вкладке История установите флаг Сохранять историю.
7. Перейдите в источник «Source», а затем в приложение источника «Application», и добавьте
экземпляр логического типа источника «ASRMB».
22
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 217 ===
3. НАСТРОЙКА ALPHA.IMITATOR В ALPHA.DEVSTUDIO
8. Перейдите в Узел Alpha.Domain «host», а затем в приложение «Application», и добавьте экземпляр
логического типа Alpha.Server «ASRMB».
Добавленному типу на вкладке Свойства укажите Представляемый объект - экземпляр логического типа
источника «ASRMB», ранее добавленный в приложение источника.
9. Инициализируйте ссылку:
вызовите контекстное меню и выполните команду Инициализировать все ссылки;
нажмите кнопку
на панели инструментов или клавишу «F5» на клавиатуре.
3.7.3. Требуемые модули Alpha.Imitator
1. Перейдите в Узел Alpha.Domain «host», а затем в Alpha.Imitator.
2. Чтобы Alpha.Imitator предоставлял данные по TCP клиенту, например Alpha.HMI.Trends, добавьте
модуль TCP Server.
3.8. Настройки для режима дополнения истории
Для работы Alpha.Imitator в режиме дополнения истории выполните следующие настройки:
настройте БД, в которую будет дополняться история;
настройте сигналы, для которых требуется дополнять историю;
настройте передачу данных через файловый интерфейс.
3.8.1. Настройка БД для дополнения истории
1. В Узле Alpha.Domain «host» перейдите в Alpha.Imitator и на элементе Модуль истории нажмите кнопку
для добавления базы данных, в которую будут дополняться пропущенные исторические данные.
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
23

=== Page 218 ===
3. НАСТРОЙКА ALPHA.IMITATOR В ALPHA.DEVSTUDIO
2. Для добавленной базы данных укажите значения свойств:
Короткое имя БД очереди - имя базы данных, в которую будет дополняться история - «default»;
Режим работы с хранилищем - «Чтение и запись».
3.8.2. Настройка сигналов для дополнения истории
Сигналам Alpha.Server, для которых требуется дополнять историю, должно быть настроено сохранение
значений в Alpha.Historian. Настройте сигналы аналогично сигналам для воспроизведения истории.
3.8.3. Настройка передачи данных через файловый интерфейс
Настройте передачу данных через файловый интерфейс между источником «Source» и Alpha.Server:
1. Перейдите в Узел Alpha.Domain «Source» и добавьте элемент Папка обмена.
2. На вкладке Свойства в значении параметра Папка укажите сетевую папку, в которую модуль TCP
Server будет сохранять файлы данных.
3. Соедините модуль TCP Server с Папкой обмена.
24
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 219 ===
3. НАСТРОЙКА ALPHA.IMITATOR В ALPHA.DEVSTUDIO
4. Перейдите в Alpha.Domain и добавьте элемент Файловый обмен.
5. Удалите связь между Адаптером Ethernet и Сетью Ethernet, и соедините Папку обмена источника
«Source» с элементом Файловый обмен.
6. Перейдите в Узел Alpha.Domain «host» и добавьте элемент Папка обмена. На вкладке Свойства в
значении параметра Папка укажите ту же сетевую папку, что задана для Папки обмена источника
«Source».
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
25

=== Page 220 ===
3. НАСТРОЙКА ALPHA.IMITATOR В ALPHA.DEVSTUDIO
7. Соедините HUB Module с Папкой обмена. Из этой папки HUB Module будет читать файлы данных.
8. Вернитесь в Alpha.Domain и соедините Папку обмена Узла Alpha.Domain «host» с элементом
Файловый обмен.
Передача данных через файловый интерфейс между источником «Source» и Alpha.Server настроена.
Теперь нужно настроить передачу данных через файловый интерфейс между Alpha.Server и Alpha.Imitator:
1. Перейдите в Узел Alpha.Domain «host» и добавьте ещё один элемент Папка обмена. На вкладке
Свойства в значении параметра Папка укажите сетевую папку, в которую модуль TCP Server
Alpha.Server будет сохранять файлы данных, а HUB Module Alpha.Imitator читать данные.
26
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 221 ===
3. НАСТРОЙКА ALPHA.IMITATOR В ALPHA.DEVSTUDIO
2. Соедините модуль TCP Server Alpha.Server и HUB Module Alpha.Imitator с добавленной Папкой
обмена.
3. Вернитесь в Alpha.Domain и соедините вторую Папку обмена Узла Alpha.Domain «host» с элементом
Файловый обмен.
3.9. Применение конфигураций Alpha.Server и
Alpha.Imitator
1. Постройте решение. Конфигурации Alpha.Server и Alpha.Imitator будут построены.
2. Перейдите в Мастер развёртывания.
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
27

=== Page 222 ===
3. НАСТРОЙКА ALPHA.IMITATOR В ALPHA.DEVSTUDIO
3. Примените конфигурации к Alpha.Server и Alpha.Imitator.
28
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 223 ===
4. НАСТРОЙКА ALPHA.IMITATOR В КОНФИГУРАТОРЕ
4. Настройка Alpha.Imitator в Конфигураторе
ОБРАТИТЕ ВНИМАНИЕ
Конфигурация Alpha.Imitator и конфигурация Alpha.Server, выполняющего обработку и запись
данных в Alpha.Historian, должны быть одинаковы.
Чтобы настроить Alpha.Imitator:
настройте конфигурацию Alpha.Server для требуемого режима работы Alpha.Imitator;
сохраните конфигурацию Alpha.Server;
загрузите сохраненную конфигурацию Alpha.Server в Alpha.Imitator.
4.1. Настройка конфигурации для режима
воспроизведения истории
Для работы Alpha.Imitator в режиме воспроизведения истории выполните следующие настройки:
настройте сигналы, для которых требуется воспроизводить историю;
в конфигурацию Alpha.Server добавьте требуемые модули;
настройте сохранение данных в имитационную БД.
4.1.1. Настройка сигналов
Сигналам Alpha.Server, для которых требуется воспроизводить историю, настройте сохранение значений в
Alpha.Historian. Для этого добавьте сигналам свойство 9001 (Historizing) со значением «True».
Например, требуется воспроизводить историю изменения значений сигнала «Process.Parameter»:
4.1.2. Требуемые модули
Добавьте в состав конфигурации следующие модули:
1. TCP Server - модуль будет предоставлять по TCP имитационные данные клиенту, например
Alpha.HMI.Trends.
2. OPC DA Server - модуль нужен для управления процессом имитации через служебные сигналы по
OPC DA с помощью OPC клиента, например OpcExplorer.
3. History Module - модуль будет получать данные из имитационной базы Alpha.Historian.
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
29

=== Page 224 ===
4. НАСТРОЙКА ALPHA.IMITATOR В КОНФИГУРАТОРЕ
4.1.3. Настройка сохранения данных в имитационную БД
Настройте сохранение данных в имитационную БД Alpha.Historian (стр. 56) для дальнейшего
воспроизведения истории с помощью Alpha.Imitator.
Чтобы настроить сохранение данных в имитационную БД Alpha.Historian:
1. В модуле History Module добавьте хранилище для имитационных данных и укажите его параметры:
Короткое имя БД очереди – «imitdb1» (имя созданной в Alpha.Historian имитационной базы (стр.
56));
Тип данных хранилища – «Имитационные данные»;
Режим работы хранилища – «Чтение и запись».
2. В хранилище добавьте базу для сохранения имитационных данных и укажите её параметры:
Хост – IP-адрес Alpha.Historian;
Короткое имя БД – «imitdb1» (имя созданной в Alpha.Historian имитационной базы (стр. 56)).
4.2. Настройка конфигурации для режима перезаписи
истории
Для работы Alpha.Imitator в режиме перезаписи истории выполните следующие настройки:
настройте сигналы, для которых требуется выполнять пересчёт и перезаписывать историю;
в конфигурацию Alpha.Server добавьте требуемые модули;
настройте сохранение данных в БД Alpha.Historian.
30
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 225 ===
4. НАСТРОЙКА ALPHA.IMITATOR В КОНФИГУРАТОРЕ
4.2.1. Настройка сигналов
Сигналам Alpha.Server, для которых требуется выполнять пересчёт и перезаписывать историю, настройте
логику вычислений и сохранение значений в Alpha.Historian. Для сохранение значений в Alpha.Historian
добавьте сигналам свойство 9001 (Historizing) со значением «True».
Например, значение сигнала «ASRMB.Item» вычисляется на основе значения сигнала «ASRMB.Recalc» по
формуле:
ASRMB.Item = ASRMB.Recalc + 10
Требуется пересчитать и перезаписать в Alpha.Historian значения сигнала «ASRMB.Item» на основе новых
значений сигнала «ASRMB.Recalc».
Настройки для сигнала «ASRMB.Item»:
Настройки для сигнала «ASRMB.Recalc»:
4.2.2. Требуемые модули
Добавьте в состав конфигурации следующие модули:
1. TCP Server - модуль будет предоставлять по TCP данные клиенту, например Alpha.HMI.Trends.
2. OPC DA Server - модуль нужен для управления процессом имитации через служебные сигналы по
OPC DA с помощью OPC клиента, например OpcExplorer..
3. Logics Module - в режиме перезаписи истории модуль будет выполнять логическую обработку
данных: пересчёт на основе параметров, значения которых задаёт пользователь.
4. History Module - модуль будет записывать пересчитанные значения в БД Alpha.Historian.
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
31

=== Page 226 ===
4. НАСТРОЙКА ALPHA.IMITATOR В КОНФИГУРАТОРЕ
4.2.3. Настройка сохранения данных в БД
Для работы Alpha.Imitator в режиме перезаписи истории настройте сохранение данных в БД Alpha.Historian.
В дальнейшем с помощью Alpha.Imitator данные этой БД могут быть пересчитаны и перезаписаны.
Чтобы настроить сохранение данных в БД Alpha.Historian:
1. В модуле History Module добавьте хранилище и укажите его параметры:
Короткое имя БД очереди – «default» (имя БД в Alpha.Historian);
Тип данных хранилища – «История значений»;
Режим работы хранилища – «Чтение и запись».
2. В хранилище добавьте базу для сохранения значений и укажите её параметры:
Хост – IP-адрес Alpha.Historian;
Короткое имя БД – «default» (имя БД в Alpha.Historian).
4.3. Настройка конфигурации для режима дополнения
истории
Для работы Alpha.Imitator в режиме дополнения истории выполните следующие настройки:
настройте сигналы, для которых требуется дополнять историю;
в конфигурацию Alpha.Server добавьте требуемые модули;
настройте сохранение данных в БД Alpha.Historian;
настройте файловый интерфейс.
32
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 227 ===
4. НАСТРОЙКА ALPHA.IMITATOR В КОНФИГУРАТОРЕ
4.3.1. Настройка сигналов
Сигналам Alpha.Server, для которых требуется дополнять историю, настройте сохранение значений в
Alpha.Historian. Для этого добавьте сигналам свойство 9001 (Historizing) со значением «True».
4.3.2. Требуемые модули
Добавьте в состав конфигурации следующие модули:
1. OPC DA Server - модуль нужен для управления процессом имитации через служебные сигналы по
OPC DA с помощью OPC клиента, например OpcExplorer.
2. HUB Module - режиме дополнения пропущенных данных модуль будет получать файлы для
дополнения пропущенных исторических данных.
3. History Module - модуль будет записывать пропущенные данные в БД Alpha.Historian.
4.3.3. Настройка сохранения данных в БД
Для работы Alpha.Imitator в режиме дополнения пропущенных данных настройте сохранение данных в БД
Alpha.Historian. В дальнейшем с помощью Alpha.Imitator пропущенные данные этой БД могут быть
дополнены.
Чтобы настроить сохранение данных в БД Alpha.Historian:
1. В модуле History Module добавьте хранилище и укажите его параметры:
Короткое имя БД очереди – «default» (имя БД в Alpha.Historian);
Тип данных хранилища – «История значений»;
Режим работы хранилища – «Чтение и запись».
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
33

=== Page 228 ===
4. НАСТРОЙКА ALPHA.IMITATOR В КОНФИГУРАТОРЕ
2. В хранилище добавьте базу для сохранения значений и укажите её параметры:
Хост – IP-адрес Alpha.Historian;
Короткое имя БД – «default» (имя БД в Alpha.Historian).
4.3.4. Настройка файлового интерфейса
Для работы Alpha.Imitator в режиме дополнения пропущенных исторических данных в состав конфигурации
Alpha.Server добавьте модуль HUB Module и выполните настройку:
1. В Общих параметрах модуля параметру Активность установите значение «Да».
2. В настройках источника в группе параметров Настройки файлового интерфейса:
В параметру Включить интерфейс установите значение «Да»;
в значении параметра Полное имя папки для чтения данных укажите путь к папке, из которой
будут читаться файлы данных.
4.4. Сохранение конфигурации Alpha.Server
Чтобы сохранить конфигурацию настроенного Alpha.Server, выполните команду меню Файл →Сохранить
конфигурацию в файл… и сохраните файл конфигурации на диске.
34
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 229 ===
4. НАСТРОЙКА ALPHA.IMITATOR В КОНФИГУРАТОРЕ
4.5. Загрузка конфигурации в Alpha.Imitator
Чтобы загрузить сохраненную конфигурацию Alpha.Server в Alpha.Imitator:
1. Подключитесь к Alpha.Imitator с помощью сервисного приложении Конфигуратор. Для подключения
укажите порт «4983».
2. Выполните команду меню Файл →Загрузить конфигурацию из файла… и выберите ранее сохраненный
файл конфигурации Alpha.Server на диске.
3. Перезапустите службу Alpha.Imitator.
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
35

=== Page 230 ===
5. СЛУЖЕБНЫЕ СИГНАЛЫALPHA.IMITATOR
5. Служебные сигналы Alpha.Imitator
При запуске Alpha.Imitator создаёт служебные сигналы для управления и контроля процессов
воспроизведения истории, коррекции исторических данных, дополнения пропущенных исторических данных.
Полный тег служебных сигналов Alpha.Imitator имеет вид:
Service.Imitation.<Имя сигнала>
Назначение служебных сигналов:
Тег и тип сигнала
Назначение
Управление сессией имитации
«BeginSession» (Uint1)
Запустить новую сессию имитации в режиме:
«0» – воспроизведение истории;
«1» – перезапись исторических данных;
«2» – дополнение пропущенных исторических данных.
«EndSession» (Bool)
Завершить сессию имитации:
«True» – завершить сессию.
«Cancel» (Bool)
Отменить сессию имитации:
«True» – отменить;
«False» – значение по умолчанию, устанавливается
после отмены сессии имитации.
Управление имитацией
«LoadData» (Bool)
Загрузить данные для воспроизведения:
«true» – загрузить данные .
Загрузка возможна только в рамках открытой сессии.
36
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 231 ===
5. СЛУЖЕБНЫЕ СИГНАЛЫALPHA.IMITATOR
Тег и тип сигнала
Назначение
«SetSpeed» (Float)
Установить скорость воспроизведения истории.
Указывается время в секундах между воспроизводимыми
значениями. Например, если задать значение «1», то будут
отображаться данные за каждую секунду; если задать значение
«10» – за каждую десятую секунду.
Сбрасывается после установки сигналов «EndSession» и
«BeginSession».
«SetCurrent» (String)
Установить текущее положение процесса воспроизведения
истории.
Перемещает текущую метку воспроизведения истории на
заданную. Задаётся в формате datetime_json.
Сбрасывается после установки сигналов «EndSession» и
«BeginSession».
«SetState» (Uint1)
Управление процессом имитации:
«0» – пауза (только для режима воспроизведения
истории);
«1» – запустить процесс имитации.
Воспроизведение истории возможно только после полной
загрузки имитационных данных.
«Commit» (Bool)
Применить результаты имитации:
«True» – сохранить результат в Alpha.Historian;
«False» – значение по умолчанию, устанавливается
после завершения сохранения.
Параметры имитации
«IntervalStart» (String)
Метка времени начала интервала имитации.
Задается в формате datetime_json. Сбрасывается после
установки сигналов «EndSession» и «BeginSession».
Значение по умолчанию: "" – левая граница отсутствует.
«SetIntervalStart» (String)
Задать метку времени начала интервала имитации.
Задается в формате datetime_json.
«IntervalEnd» (String)
Метка времени конца интервала имитации.
Задается в формате datetime_json. Сбрасывается после
установки сигналов «EndSession» и «BeginSession».
Значение по умолчанию: "" – правая граница отсутствует.
«SetIntervalEnd» (String)
Задать метку времени конца интервала имитации.
Задается в формате datetime_json.
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
37

=== Page 232 ===
5. СЛУЖЕБНЫЕ СИГНАЛЫALPHA.IMITATOR
Тег и тип сигнала
Назначение
«Filter» (String)
Фильтр по тегам.
Сбрасывается после установки сигналов «EndSession» и
«BeginSession».
Значение по умолчанию: "" – все теги.
«SetFilter» (String)
Установить фильтр по тегам.
Контроль текущего состояния сессии имитации
«DataLoaded» (Uint1)
Процент готовности данных к воспроизведению от «0» до «100».
Сбрасывается после установки сигналов «EndSession» и
«BeginSession».
Значение по умолчанию: «0».
«Current» (String)
Текущее положение процесса воспроизведения истории.
Отображается в формате datetime_json. Сбрасывается после
установки сигналов «EndSession» и «BeginSession».
Значение по умолчанию: "".
«Speed» (Float)
Скорость воспроизведения истории.
Время в секундах между воспроизводимыми значениями.
Сбрасывается после установки сигналов «EndSession» и
«BeginSession».
Значение по умолчанию: «1».
«State» (Uint1)
Статус имитации:
«0» – остановлено или завершено;
«1» – воспроизводится;
«2» - успешно завершено (для режима перезаписи и
дополнения истории);
«3» - завершено с ошибкой (для режима перезаписи и
дополнения истории).
Сбрасывается после установки сигналов «EndSession» и
«BeginSession».
Значение по умолчанию: «0».
«SessionInProgress» (Bool)
Флаг наличия активной сессии.
Устанавливается после установки сигнала «BeginSession»,
сбрасывается после установки сигнала «EndSession».
Значение по умолчанию: «False».
Информация об ошибках
«LastError» (String)
Информация о последней возникшей ошибке.
Работа с данными
38
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 233 ===
5. СЛУЖЕБНЫЕ СИГНАЛЫALPHA.IMITATOR
Тег и тип сигнала
Назначение
«Override» (String)
Задать массив перезаписываемых значений тега. Задается в
формате trend_json.
Позволяет перезаписать значения нескольких тегов. Для этого
следует в значении сигнала «Override» в формате trend_json
поочерёдно задать массивы перезаписываемых значений
каждого тега.
«GetOverriden» (Bool)
Получить массив перезаписываемых тегов:
«True» – получить массив;
«False» – значение по умолчанию.
«GetOverridenResponse» (String)
Массив перезаписываемых тегов в формате:
["Tag":"<string>", …]
«ReadOverriden» (String)
Получить массив перезаписываемых значений:
{"Tag": "<string>"}
«ReadOverridenResponse» (String)
Массив перезаписываемых значений. Строка в формате trend_
json со значениями за интервал, заданный в сигналах
«IntervalStart» и «IntervalEnd».
«ReadHistory» (String)
Запросить историю значений тега:
{"Tag": "<string>"}
«ReadHistoryResponse» (String)
Массив исторических значений. Строка в формате trend_json со
значениями за интервал, заданный в сигналах «IntervalStart»
и «IntervalEnd».
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
39

=== Page 234 ===
6. РАБОТА С ALPHA.IMITATOR
6. Работа с Alpha.Imitator
Управление и контроль процессами воспроизведения истории, коррекции исторических данных, дополнения
пропущенных исторических данных выполняется с помощью служебных сигналов Alpha.Imitator.
Чтобы изменять и контролировать значения служебных сигналов, подключитесь к Alpha.Imitator, с помощью
OPC клиента, например OpcExplorer. Для этого подключитесь к источнику «AP.OPCDAServer.Imitator».
Подробная информация о работе Alpha.Imitator выводится в журнал приложений. Для просмотра журнала
запустите приложение EventLogViewer.
6.1. Воспроизведение истории
Для просмотра воспроизведения истории с помощью Alpha.Imitator запустите приложение
Alpha.HMI.Trends, у которого в качестве источника данных должен быть настроен Alpha.Imitator.
В оперативном режиме на трендовое поле добавьте сигналы из дерева Alpha.Imitator, для которых нужно
воспроизвести историю изменения значений.
ОБРАТИТЕ ВНИМАНИЕ
В имитационной базе должна быть история изменений по добавленным сигналам: значения сигналов
изменялись после настроек Alpha.Historian и Alpha.Server.
40
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 235 ===
6. РАБОТА С ALPHA.IMITATOR
В OpcExplorer в Инспектор добавьте служебные сигналы для управления и контроля процесса
воспроизведения истории:
«SessionInProgress» - флаг наличия активной сессии;
«EndSession» - команда завершения сессии проигрывания;
«BeginSession» - команда запуска сессии имитации;
«SetIntervalStart»- задать метку времени начала имитируемого интервала;
«SetIntervalEnd» - задать метку времени конца имитируемого интервала;
«SetSpeed» - задать скорость проигрывания;
«IntervalStart» - метка времени начала интервала проигрывания;
«IntervalEnd» - метка времени конца интервала проигрывания;
«Speed» - текущая скорость проигрывания;
«LoadData» - загрузить данные для проигрывания;
«DataLoaded» - процент готовности данных к проигрыванию;
«SetState» - запустить процесс имитации;
«Current» - текущее положение процесса проигрывания;
«State» - статус процесса имитации.
Для воспроизведения истории:
1. Убедитесь, что нет активной сессии имитации:
«SessionInProgress» == «False».
Если «SessionInProgress» == «True», то завершите текущую сессию имитации, установив значение
сигнала:
«EndSession» = «True».
2. Запустите новую сессию имитации в режиме воспроизведения истории, установив значение сигнала:
«BeginSession» = «0».
При этом активируется флаг наличия активной сессии «SessionInProgress» == «True».
3. Задайте временной интервал в формате datetime_json, за который требуется воспроизвести историю,
а также скорость проигрывания, установив значения сигналов:
«SetIntervalStart»;
«SetIntervalEnd»;
«SetSpeed».
Пример метки времени в формате datetime_json, соответствующий времени «11.10.2023 17:32:01.1»
в часовом поясе UTC+7:
{"y":2023,"mo":10,"d":11,"h":10,"m":32,"s":1,"ms":1}
Сигналы устанавливают значения соответствующих сигналов «IntervalStart», «IntervalEnd» и
«Speed».
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
41

=== Page 236 ===
6. РАБОТА С ALPHA.IMITATOR
4. Загрузите данные для воспроизведения истории, установив значение сигнала:
«LoadData» = «True».
Процент загруженных данных отображается в значении сигнала «DataLoaded».
5. После полной загрузки данных («DataLoaded» == «100») запустите воспроизведение истории,
установив значение сигнала:
«SetState» = «1».
В процессе воспроизведения истории текущее положение процесса воспроизведения отображается в
значении сигнала «Current», а статус воспроизведения «State» == «1».
На трендовом поле Alpha.HMI.Trends в оперативном режиме отображается изменение значений
сигналов за воспроизводимый период времени.
42
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 237 ===
6. РАБОТА С ALPHA.IMITATOR
6. Чтобы завершить сессию воспроизведения истории, установите значение сигнала:
«EndSession» = «True».
При этом сбрасываются значения сигналов «IntervalStart», «IntervalEnd», «Current», а также
устанавливаются следующие значения сигналов:
«State» = «0»;
«Speed» = «1»;
«SessionInProgress» = «False».
ПРИМЕЧАНИЕ
В процессе воспроизведения истории («State» == «1») возможно:
1. Изменение скорости воспроизведения в сигнале «SetSpeed».
2. Изменение текущего положения воспроизведения в сигнале «SetCurrent».
3. Приостановка воспроизведения (пауза): «SetState» = «0».
4. Завершение сессии воспроизведения: «EndSession» = «True».
При достижении конца воспроизводимого интервала или приостановке воспроизведения («State» ==
«0») возможно:
1. Изменение скорости воспроизведения истории в сигнале «SetSpeed».
2. Изменение текущего положения воспроизведения в сигнале «SetCurrent».
3. Возобновление воспроизведения: «SetState» = «1».
4. Завершение сессии воспроизведения: «EndSession» = «True».
6.2. Перезапись исторических данных
В Alpha.Historian хранится некоторая история изменения сигнала «ASRMB.Recalc» и вычисленных значений
сигнала «ASRMB.Item».
Значение сигнала «ASRMB.Item» вычисляется на основе значения сигнала «ASRMB.Recalc» по формуле:
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
43

=== Page 238 ===
6. РАБОТА С ALPHA.IMITATOR
ASRMB.Item = ASRMB.Recalc + 10
Требуется пересчитать и перезаписать в Alpha.Historian значения сигнала «ASRMB.Item» на основе новых
значений сигнала «ASRMB.Recalc».
6.2.1. Перезапись единственного значения
В OpcExplorer в Инспектор добавьте служебные сигналы для управления и контроля процесса перезаписи
исторических данных:
«SessionInProgress» - флаг наличия активной сессии;
«BeginSession» - команда запуска сессии имитации;
«Cancel» - отменить сессию имитации;
«SetIntervalStart» - задать метку времени начала перезаписываемого интервала;
«SetIntervalEnd» - задать метку времени конца перезаписываемого интервала;
«IntervalStart» - метка времени начала перезаписываемого интервала;
«IntervalEnd» - метка времени конца перезаписываемого интервала;
«ReadHistory» - запросить историю значений тега;
«ReadHistoryResponse» - список исторческих значений;
«SetState» - запустить процесс имитации;
«State» - статус процесса имитации;
«Commit» - применить результаты имитации.
Для перезаписи единственного значения:
1. Переведите Alpha.Imitator в работу, установив значение сигнала «Service.State.Server.Set» =
«True».
2. Убедитесь, что нет активной сессии имитации:
«SessionInProgress» == «False».
Если «SessionInProgress» == «True», то отмените текущую сессию имитации, установив значение
сигнала:
«Cancel» = «True».
3. Запустите новую сессию имитации в режиме перезаписи исторических данных, установив значение
сигнала
«BeginSession» = «1».
4. Задайте временной интервал, за который требуется перезаписать данные в Alpha.Historian, установив
значения сигналов:
«SetIntervalStart»;
«SetIntervalEnd».
44
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 239 ===
6. РАБОТА С ALPHA.IMITATOR
Значения в указанных сигналах задаются в формате datetime_json по времени UTC. Например,
требуется перезаписать данные в интервале с «12.10.2023 10:38:39.1» по «12.10.2023 10:38:40.1»:
в значение сигнала «SetIntervalStart» запишите строку:
{"y":2023,"mo":10,"d":12,"h":3,"m":38,"s":39,"ms":1}
в значение сигнала «SetIntervalEnd» запишите строку:
{"y":2023,"mo":10,"d":12,"h":3,"m":38,"s":40,"ms":1}
Сигналы устанавливают значения соответствующих сигналов «IntervalStart» и «IntervalEnd».
5. Проверьте значения тегов в Alpha.Historian за заданный временной интервал. Для этого в сигнале
«ReadHistory» укажите тег в формате:
{"Tag":"ASRMB.Recalc"}
В значении сигнала «ReadHistoryResponse» отобразятся значения тега за указанный интервал.
История значений тега «ASRMB.Recalc» в указанном интервале:
История значений тега «ASRMB.Item» в указанном интервале:
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
45

=== Page 240 ===
6. РАБОТА С ALPHA.IMITATOR
Графики сигналов имеют вид:
6. Установите новое значение тегу «ASRMB.Recalc», на основе которого требуется пересчитать и
перезаписать значение тега «ASRMB.Item». Например, «ASRMB.Recalc» == «15».
7. Запустите имитацию, установив значение сигнала:
«SetState» = «1».
В результате имитации значение тега «ASRMB.Item» будет пересчитано, а статус процесса имитации
примет значение «State» == «2».
46
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 241 ===
6. РАБОТА С ALPHA.IMITATOR
8. Сохраните результат имитации в Alpha.Historian, установив значение сигнала:
«Commit» = «True».
Новые значения тегов «ASRMB.Recalc» и «ASRMB.Item» будут перезаписаны в Alpha.Historian. При этом
сбрасываются значения сигналов «IntervalStart» и «IntervalEnd», а также устанавливаются
следующие значения сигналов:
«State» = «0»;
«SessionInProgress» = «False».
Чтобы проверить запись новых значений тегов в Alpha.Historian за заданный временной интервал:
1. Запустите сессию имитации: «BeginSession» = «1».
2. Задайте временной интервал:
в значение сигнала «SetIntervalStart» запишите строку:
{"y":2023,"mo":10,"d":12,"h":3,"m":38,"s":39,"ms":1}
в значение сигнала «SetIntervalEnd» запишите строку:
{"y":2023,"mo":10,"d":12,"h":3,"m":38,"s":40,"ms":1}
3. В сигнале «ReadHistory» укажите тег, после чего сигнале «ReadHistoryResponse» отобразятся
значения тега за указанный интервал.
История значений тега «ASRMB.Recalc» в указанном интервале:
История значений тега «ASRMB.Item» в указанном интервале:
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
47

=== Page 242 ===
6. РАБОТА С ALPHA.IMITATOR
Графики сигналов с перезаписанными значениями примут вид:
6.2.2. Перезапись массива данных
В OpcExplorer в Инспектор добавьте служебные сигналы для управления и контроля процесса перезаписи
исторических данных:
«SessionInProgress» - флаг наличия активной сессии;
«BeginSession» - команда запуска сессии имитации;
«Cancel» - отменить сессию имитации;
«SetIntervalStart» - задать метку времени начала перезаписываемого интервала;
«SetIntervalEnd» - задать метку времени конца перезаписываемого интервала;
«IntervalStart» - метка времени начала перезаписываемого интервала;
«IntervalEnd» - метка времени конца перезаписываемого интервала;
48
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 243 ===
6. РАБОТА С ALPHA.IMITATOR
«ReadHistory» - запросить список исторических значений;
«ReadHistoryResponse» - список исторических значений;
«Override» - задать перезаписываемые сигналы;
«ReadOverriden» - запросить список переопределяемых значений;
«ReadOverridenResponse» - список переопределяемых значений;
«GetOverriden» - запросить список переопределяемых тегов;
«GetOverridenResponse» - список переопределяемых тегов;
«SetState» - запустить процесс имитации;
«State» - статус процесса имитации;
«Commit» - применить результаты имитации.
Для перезаписи массива значений:
1. Переведите Alpha.Imitator в работу, установив значение сигнала «Service.State.Server.Set» =
«True».
2. Убедитесь, что нет активной сессии имитации:
«SessionInProgress» == «False».
Если «SessionInProgress» == «True», то отмените текущую сессию имитации, установив значение
сигнала:
«Cancel» = «True».
3. Запустите новую сессию имитации в режиме перезаписи исторических днных, установив значение
сигнала
«BeginSession» = «1».
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
49

=== Page 244 ===
6. РАБОТА С ALPHA.IMITATOR
4. Задайте временной интервал, за который требуется перезаписать данные в Alpha.Historian, установив
значения сигналов:
«SetIntervalStart»;
«SetIntervalEnd».
Значения в указанных сигналах задаются в формате datetime_json по времени UTC. Например,
требуется перезаписать данные в интервале с «12.10.2023 10:56:19.1» по «12.10.2023 10:56:30.1»:
в значение сигнала «SetIntervalStart» запишите строку:
{"y":2023,"mo":10,"d":12,"h":3,"m":56,"s":19,"ms":1}
в значение сигнала «SetIntervalEnd» запишите строку:
{"y":2023,"mo":10,"d":12,"h":3,"m":56,"s":30,"ms":1}
Сигналы устанавливают значения соответствующих сигналов «IntervalStart» и «IntervalEnd».
5. Проверьте значения тегов в Alpha.Historian за заданный временной интервал. Для этого в сигнале
«ReadHistory» укажите тег в формате:
{"Tag":"ASRMB.Recalc"}
В значении сигнала «ReadHistoryResponse» отобразятся значения тега за указанный интервал.
История значений тега «ASRMB.Recalc» в указанном интервале содержит две записи:
50
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 245 ===
6. РАБОТА С ALPHA.IMITATOR
История значений тега «ASRMB.Item» в указанном интервале содержит две записи:
Графики сигналов имеют вид:
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
51

=== Page 246 ===
6. РАБОТА С ALPHA.IMITATOR
6. Установите новые значения тега «ASRMB.Recalc», на основе которых требуется пересчитать и
перезаписать значения тега «ASRMB.Item». Например, тегу «ASRMB.Recalc» установите значения «15» и
«0», вместо имеющихся «2» и «10». Для этого в сигнал «Override» запишите команду на перезапись
массива значений в формате trend_json:
{"Tag": "ASRMB.Recalc", "Add": [{"v": "15", "q": "216", "t":
{"y":2023,"mo":10,"d":12,"h":3,"m":56,"s":19,"ms":1}}, {"v": "0", "q": "216", "t":
{"y":2023,"mo":10,"d":12,"h":3,"m":56,"s":29,"ms":1}}]}
7. Убедитесь, что для перезаписи подготовлены верные значения - «15» и «0». Для этого укажите в
сигнале «ReadOverriden» тег, значения которого требуется перезаписать, в формате:
{"Tag":"ASRMB.Recalc"}
Массив значений, подготовленный для перезаписи, будет выведен в значении сигнала
«ReadOverridenResponse».
8. Убедитесь, что список перезаписываемых тегов верен, установив значение сигнала «GetOverriden» =
«True». Список перезаписываемых тегов будет выведен в значении сигнала «GetOverridenResponse».
52
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 247 ===
6. РАБОТА С ALPHA.IMITATOR
9. Запустите имитацию, установив значение сигнала:
«SetState» = «1».
В результате имитации заданные значения тега «ASRMB.Recalc» и значения тега «ASRMB.Item» будут
пересчитаны и перезаписаны. В сигналах будут отображаться последние перезаписанные значения из
массива, а статус процесса имитации примет значение «State» == «2».
10. Сохраните результат имитации в Alpha.Historian, установив значение сигнала: «Commit» = «True».
Массивы новых значений тегов «ASRMB.Recalc» и «ASRMB.Item» будут перезаписаны в Alpha.Historian.
При этом сбрасываются значения сигналов «IntervalStart», «IntervalEnd», «Current», а также
устанавливаются следующие значения сигналов:
«State» = «0»;
«SessionInProgress» = «False».
Чтобы проверить запись массивов новых значений тегов в Alpha.Historian за заданный временной интервал:
1. Запустите сессию имитации: «BeginSession» = «1».
2. Задайте временной интервал:
в значение сигнала «SetIntervalStart» запишите строку:
{"y":2023,"mo":10,"d":12,"h":3,"m":38,"s":39,"ms":1}
в значение сигнала «SetIntervalEnd» запишите строку:
{"y":2023,"mo":10,"d":12,"h":3,"m":38,"s":40,"ms":1}
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
53

=== Page 248 ===
6. РАБОТА С ALPHA.IMITATOR
3. В сигнале «ReadHistory» укажите тег, после чего в сигнале «ReadHistoryResponse» отобразятся
значения тега за указанный интервал.
История значений тега «ASRMB.Recalc» в указанном интервале:
История значений тега «ASRMB.Item» в указанном интервале:
54
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 249 ===
6. РАБОТА С ALPHA.IMITATOR
Графики сигналов с перезаписанными значениями примут вид:
6.3. Дополнение пропущенных исторических данных
Чтобы записать отсутствующие данные в Alpha.Historian:
1. Определите промежуток времени, за который отсутствуют данные в Alpha.Historian.
2. Остановите Alpha.Server.
3. В папку, указанную в настройках источника HUB Module в Alpha.Imitator, поместите файлы данных,
которые не были переданы от нижестоящих систем за интересующий промежуток времени (в примере
настройки папка C:\Backfilling).
ОБРАТИТЕ ВНИМАНИЕ
Файлы данных, из которых будет дополнена история, это DAT-файлы (*.dat), содержащие
значения сигналов. Файлы данных следует скопировать из папки, в которую они были
сгенерированы нижестоящей системой.
4. Переведите Alpha.Imitator в работу, установив значение сигнала «Service.State.Server.Set» =
«True».
5. Откройте новую сессию имитации в режиме дополнения пропущенных исторических данных,
установив значение сигнала «BeginSession» = «2».
При открытии сессии имитации в режиме дополнения пропущенных исторических данных Alpha.Imitator
начинает разбор файлов данных и записывает в Alpha.Historian полученные значения и пересчитанные
зависимые параметры, заполняя промежутки времени, за которые отсутствовали данные в истории.
Прочитанные файлы удаляются из папки автоматически.
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
55

=== Page 250 ===
7. ПРИЛОЖЕНИЯ
7. Приложения
Приложение A: Создание имитационной базы данных
Для воспроизведения истории с помощью Alpha.Imitator необходимо настроить сохранение данных
Alpha.Server в отдельную базу Alpha.Historian, из которой Alpha.Imitator будет получать данные для
воспроизведения истории. Такая база данных называется имитационной.
Чтобы создать имитационную базу данных в Alpha.Historian:
1. Откройте файл конфигурации Alpha.Historian.Server.xml (по умолчанию расположен в папке
C:\Program Files\Automiq\Alpha.Historian).
2. Добавьте имитационную базу данных, например, «imitdb1».
<?xml version="1.0" encoding="utf-8"?>
<Alpha.Historian.Server StatPort="3388"
DefaultPrimaryDir="C:\Alpha.Historian\Databases">
<tcp-server default-port=4949 idle-sessions-count=1 idle-sessions-
timeout=15>
<server-endpoint host="0.0.0.0" />
</tcp-server>
<Bases>
<Base Alias="default" />
<Base Alias="imitdb1" />
</Bases>
</Alpha.Historian.Server>
3. Сохраните изменения в файле Alpha.Historian.Server.xml.
4. Перезапустите службу Alpha.Historian.Server.
56
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 251 ===
7. ПРИЛОЖЕНИЯ
Приложение B: Формат datetime_json
Метка времени задаётся и отображается по времени UTC в служебных сигналах в формате datetime_json и
имеет вид:
{"y":<uint>,"mo":<uint>,"d":<uint>,"h":<uint>,"m":<uint>,"s":<uint>,"ms":<uint>}
где:
у – год;
mo – месяц;
d – день;
h – часы;
m – минуты;
s – секунды;
ms – миллисекунды.
ОБРАТИТЕ ВНИМАНИЕ
Заполнение всех полей необязательно, при этом для пропущенных полей метки времени
применяется текущая дата и время «00:00:00.000».
ПРИМЕР
Метка времени:
{"y":2023,"mo":10,"d":9,"h":10,"m":49,"s":15,"ms":2}
соответствует «9.10.2023 17:49:15.2» в часовом поясе UTC+7.
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА
57

=== Page 252 ===
7. ПРИЛОЖЕНИЯ
Приложение C: Формат trend_json
Массив данных для перезаписи задаётся в служебных сигналах в формате trend_json и имеет вид:
{
"Tag":"<string>",
"Add":[{"v": "<string>", "q": "<uint2>", "t": {datetime_json}}, {…}, …],
"Update":[{"v": "<string>", "q": "<uint2>", "t": {datetime_json}}, {…}, …],
"Remove":[{"v": "<string>", "q": "<uint2>", "t": {datetime_json}}, {…}, …],
"RemoveRange":{"begin": {datetime_json}, "end": {datetime_json}},
"RemoveFromOverriden":true,
"Values":[{"v": "<string>", "q": "<uint2>", "t": {datetime_json}}, {…}, …]
}
где Tag – тег сигнала, для которого задается массив значений.
Остальные параметры могут использоваться в следующих комбинациях:
1. Установка тренда (все параметры – необязательные):
Add – массив добавляемых точек тренда;
Update – массив переопределяемых точек тренда;
Remove – массив удаляемых точек тренда;
RemoveRange – удаление точек тренда на указанном интервале.
ОБРАТИТЕ ВНИМАНИЕ
Команды Add, Update, Remove и RemoveRange применяются для формирования нового набора
данных, который в ходе имитации будет записан в Alpha.Historian.
2. Возврат тренда:
Values – массив возвращаемых точек тренда при запросе.
3. Исключить тег из списка перезаписываемых:
RemoveFromOverriden.
ПРИМЕЧАНИЕ
Точка тренда – значение (V), качество (Q) и метка времени (T – задается в формате datetime_json).
Пример массива данных для перезаписи:
{"Tag": "ASRMB.Item.Recalc", "Add": [{"v": "100", "q": "216", "t": {"y":2023, "mo":10,
"d":9, "h":10, "m":3, "s":23, "ms":452}}, {"v": "190", "q": "216", "t": {"y":2023, "mo":10,
"d":9, "h":10, "m":3, "s":37, "ms":168}}, {"v": "300", "q": "216", "t": {"y":2023, "mo":10,
"d":9, "h":10, "m":3, "s":30, "ms":384}}}]}
что соответствует записи в тег «ASRMB.Item.Recalc» массива данных (время по UTC):
значение «100», качество «216», метка времени «9.10.2023 10:03:23.452»;
значение «300», качество «216», метка времени «9.10.2023 10:03:30.384»;
значение «190», качество «216», метка времени «9.10.2023 10:03:37.168».
58
ALPHA.IMITATOR. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 253 ===
Программный комплекс Альфа платформа
Alpha.Server 6.4
История изменений
Редакция
Соответствует версии ПО
7. Предварительная
6.4.28

=== Page 254 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
История изменений
6.4
6.4.7
ОБРАТИТЕ ВНИМАНИЕ
Конфигурирование Alpha.Server 6.4.7 возможно только в Alpha.DevStudio 3.28.2.
Ранее созданные конфигурации продолжат работать на Alpha.Server 6.4.7, но при изменении
конфигурации в Alpha.DevStudio3.28.2 проект будет сконвертирован в части буферирования и
модуля истории - множества будут преобразованы к новому формату.
Новые возможности
Общий механизм фильтрации значений
Реализована фильтрация значений на основе механизма множеств. Множество - это некоторая
совокупность источников данных с определенными допусками. В качестве источников данных пока
могут выступать только сигналы. Множество получает данные от источников и выдает их
потребителям, согласно настройкам. Параметры фильтрации значений указываются для множеств
и позволяют настраивать фильтрацию для различных потребителей, а также настройку получения
данных для этих потребителей.
Потребителями данных от множеств выступают:
Модуль истории. Множествами заменен механизм допусков/повторов при записи в историю.
TCP Server. Теперь можно указать из какого множества выдавать данные для клиента.
Буфер. Источником данных для буферов теперь являются множества.
UNET Client
Реализована возможность обмена данными с контроллерами TREI по протоколу UNET2.
HUB
Реализована возможность возобновления и приостановки существующей подписки вместо
отписки/переподписки. При значении «Приостановить подписку» параметра Работа в резерве:
при переходе в резерв отправляется команда приостановки подписки;
при переходе в работу - команда возобновления подписки.
Реализована аутентификация в сервере источника по паролю.
TCP Server
Реализована аутентификация известного клиента по паролю.
Подсистема резервирования
Реализован механизм согласования конфигураций в резервной паре.
Для резервной пары серверов добавлен режим ожидания, при котором оба сервера находятся в
состоянии Приостановленный. Переход в данный режим и выход из него выполняются только по
командам через служебные сигналы.
Улучшения
2
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 255 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
TCP Server
Запрет на запись анонимным клиентам Alpha.Link теперь установлен по умолчанию.
Уменьшена задержка между отправками изменений значений клиентам.
HUB
В режиме работы в резерве «Приостановить подписку» при переходе из режима РЕЗЕРВ в режим
РАБОТА модуль HUB теперь запрашивает актуальные значения у активного сервера каждого
источника.
В модуле HUB теперь не создаётся читатель буфера, если нет источников буферируемых
данных.
Ускорено получение буферируемых данных.
Модуль логики
Уменьшено потребление памяти модулем в составе Alpha.Server и Alpha.AccessPoint.
Конфигуратор
Реализована возможность просмотра информации о конфигурации Alpha.Server.
Syslog Client
В статистике модуля теперь отображаются данные получателя.
Исправленные ошибки
UNET Client
Устранена ошибка, из-за которой в редких случаях Alpha.Server мог завершать работу.
HUB
Исправлена ошибка при планировании позиции чтения с неактивного буфера.
Модуль не подписывался на оперативные сигналы, если был подключен к TCP Server до его
перехода в работу.
После перезагрузки модуля прекращалось чтение данных буфера.
При запуске Alpha.Server завершался поток формирования кэша буфера при большом
количестве буферируемых элементов.
В редких случаях Alpha.Server зависал при остановке после завершения работы модуля HUB.
Устранена ошибка, возникавшая при чтении из буфера, если буфер ещё не содержал данных.
Исправлены ошибки, которые приводили к повторному считыванию буфера.
OPC AE Server
Исправлена ошибка, приводившая к нарушению целостности журнала OAT.
Alpha.Server
Устранено зависание обработки данных, которое приводило к неконтролируемому росту
потребления памяти.
Устранена несовместимость ресурсов в конфигурациях, созданных инструментами архитектур
x64 и x86.
6.4.9
ОБРАТИТЕ ВНИМАНИЕ
Конфигурирование Alpha.Server 6.4.9 возможно только в Alpha.DevStudio 3.28.3.
Ранее созданные конфигурации продолжат работать на Alpha.Server 6.4.9, но при изменении
конфигурации в Alpha.DevStudio 3.28.3 проект будет сконвертирован в части буферирования и
модуля истории - множества будут преобразованы к новому формату.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
3

=== Page 256 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Улучшения
Подсистема буферизации данных
Повышена производительность операции планирования вычитывания буфера.
Исправленные ошибки
Подсистема буферизации данных
Устранено ошибочное повторное вычитывание региона буфера.
HUB
Устранены незапланированные смены сервера, с которого читается буфер, если поставщик
буфера представлен парой реплицируемых серверов.
6.4.10
ОБРАТИТЕ ВНИМАНИЕ
Пользователям Alpha.Server версии 6.4.0 и выше, использующим в конфигурации модуль OPC UA
Client, рекомендуем безотлагательно произвести обновление до версии 6.4.10 для исключения
возможной отправки модулем OPC UA Client, находящимся в резерве, команд в UA Server.
Подробности возможного возникновения проблемы на Alpha.Server версии 6.4.0 и выше смотрите в
разделе "Исправленные ошибки" модуля OPC UA Client настоящей новости.
Исправленные ошибки
OPC UA Client
Находясь в резерве, модуль отправлял в UA Server уже отправленные ранее команды, получив
их по каналу репликации от основного Alpha.Server после перезапуска Alpha.Server, в составе
которого он функционирует:
В транзакционной модели исполнения модуль отправлял такие команды только для
нереплицируемых сигналов.
В модели исполнения по умолчанию модуль отправлял такие команды как для
реплицируемых сигналов, так и для нереплицируемых.
Дополнительным условием отправки таких команд являлось значение «Запрашивать данные»,
установленное для режима работы модуля в резерве.
В режиме работы в резерве «Закрывать соединение» после двойного резервного перехода
модуль переставал обмениваться данными с UA Server.
6.4.11
Улучшение
Подсистема буферизации данных
Добавлена возможность уменьшения файлов буфера при старте сервера, если это возможно
технически.
Исправленные ошибки
Подсистема буферизации данных
Последнее отфильтрованное по времени значение сигнала не записывалось в буфер, если по
сигналу больше не было изменений.
4
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 257 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
HUB
В редких случаях модуль мог ошибочно устанавливать плохое качество сигналам при
восстановлении связи.
Добавлены доработки Alpha.Server версий 6.3.13 - 6.3.15
Улучшения
SNMP Manager
Для агента добавлена возможность использования контекста для разграничения доступа к
нескольким физическим/логическим устройствам.
Добавлена возможность сбрасывать сохраненное время агента при потери связи.
Используется для агентов, неправильно считающих перезагрузки.
EtherNet/IP Scanner
Реализована возможность настройки таймаута ожидания ответа на запрос.
Исправленные ошибки
Модуль истории, TCP Server, Модуль логики
Устранены проблемы, из-за которых в редких случаях Alpha.Server мог прекращать работу.
OPC UA Client
В режиме работы в резерве «Закрывать соединение» после двойного резервного перехода
модуль переставал обмениваться данными с UA Server.
Modbus TCP Master
Для сигналов типа String не учитывалось значение параметра Байт в слове.
Модуль логики
Устранена ошибка модуля логики "Не найден зарегистрированный член типа" при
использовании в проекте логических типов.
Модуль истории
Иногда Alpha.Server мог завершать работу при остановке модуля истории.
Устранена причина нарушения целостности OAT.
OPC AE Server
Повторно генерировались события по подусловию Enumeration при резервном переходе.
Генерировалось событие по подусловию Deviation при отсутствии предыдущего значения
сигнала.
TCP Server, HUB
Устранены причины, из-за которых обмен данными между Alpha.Server и
Alpha.AccessPoint мог выполняться некорректно.
6.4.12
Исправленные ошибки
Подсистема буферизации данных
Не выполнялась операция LookForward, если клиент имел нулевую позицию. Нулевая позиция
клиента возможна в редких случаях, когда клиент подключился к буферу раньше, чем в буфер
попали данные.
Исправлена ошибка планировщика подписок на сигналы, из-за которой могло не
восстанавливается качество буферизуемых сигналов.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
5

=== Page 258 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
6.4.13
Улучшения
OPC UA Client, OPC UA Server
Максимальное значение параметра Размер очереди уведомлений увеличено до «1000».
OPC UA Client
Для группы серверов добавлена возможность указывать количество отсчётов таймера жизни
подписки, после которого подписка будет удалена.
Исправленная ошибка
IEC-104 Master
Исправлена ошибка, из-за которой могла не активироваться станция.
6.4.14
Улучшения
Modbus RTU Master, Modbus RTU Slave, Modbus TCP Master, Modbus TCP Slave
Добавлена возможность изменения порядка байт в слове для протокольных типов STR и STR-
COMMAND.
IEC-104 Master
Добавлена возможность указывать необходимость отправки команды общего опроса при
установлении связи по каналу.
OPC UA Client
Для группы серверов добавлена возможность указывать количество отсчётов таймера жизни
подписки, после которого подписка будет удалена.
Исправленные ошибки
Alpha.Server
Исправлена ошибка, из-за которой Alpha.Server иногда мог завершать работу при остановке.
TCP Server
Потребители не получали данные буфера после восстановления связи при включенной
настройке Выполнять подключение к потребителю.
IEC-104 Master
Исправлена ошибка, из-за которой могла не активироваться станция.
6.4.15
Исправленная ошибка
UNET Client
Модуль ошибочно игнорировал изменение CustomInfo, если не было изменений других свойств
сигнала.
6.4.16
Улучшения
6
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 259 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
OPC UA Server, OPC UA Client
Поддержана система управления сертификатами "CA Signed Certificate management".
OPC UA Server
Поддержаны политики безопасности Aes128-Sha256-RsaOaep, Basic256Sha256, Aes256-Sha256-
RsaPss согласно спецификации OPC UA.
Добавлены доработки Alpha.Server версии 6.3.22
Улучшение
IEC-104 Master
Реализован новый алгоритм работы очереди входящих данных.
Исправленные ошибки
EtherNet/IP Scanner
Alpha.Server завершал работу при разрыве связи с эмулятором.
IEC-104 Master
Модуль не устанавливал плохое качество сигналам при разрыве связи со станцией в режиме
Один в работе, не поддерживать соединение по остальным.
При возникновении ошибок протокола модуль не разрывал соединение и продолжал работу
по тому же каналу, но записывал сообщения о разрыве соединения в журнал работы модуля.
Теперь при ошибках протокола модуль разрывает соединение, открывает его заново и
продолжает работу.
Modbus RTU Slave, Modbus TCP Slave
Модули ошибочно добавляли в конец строки символ '\0' в кодировках utf8 и windows-1251,
если длина строки была нечетным числом.
Siemens S7 Client
При получении строки с ПЛК значение в Alpha.Server могло быть некорректным.
Alpha.Server
Устранены ошибки, возникавшие при использовании в вычислениях элементов массива.
6.4.17
Улучшения
TCP Server, HUB
Реализован механизм идентификации экземпляров и каналов в подключении HUB-TCP.
Реализованы служебные сигналы диагностики каналов связи с потребителем/источником.
ОБРАТИТЕ ВНИМАНИЕ
Изменилась структура конфигурации модулей.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
7

=== Page 260 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Alpha.Server
Идентификатор экземпляра Alpha.Server теперь задаётся при развертывании конфигурации из
Alpha.DevStudio.
Для экземпляра Alpha.Server определяется файл *.json, в котором будут хранится параметры
экземпляра. Файл располагается в папке экземпляра. Имя файла соответствует имени службы.
ВАЖНО
При использовании Alpha.Server 6.4.17:
Если необходимо сохранить существующий идентификатор экземпляра сервера
(используется при буферизации), то в качестве идентификатора элемента в проекте
Alpha.DevStudio используйте InstanceId из файла настройки сервера *.xml.
Если нет необходимости сохранять идентификатор, то удалите InstanceId из файла
настройки сервера *.xml.
Добавлены доработки Alpha.Server версий 6.3.23 и 6.3.24
Новая возможность
Реализован новый модуль GenericDeviceComm, с помощью которого Alpha.Server может
обмениваться данными с устройствами по DCON.
Исправленные ошибки
OPC AE Server, Модуль логики
Исправлены ошибки, из-за которых в некоторых случаях могли прекращаться генерация
событий и выполнение вычислений, а Alpha.Server мог завершать работу или зависать при
остановке.
EtherNet/IP Scanner
Модуль не инициализировался, если в конфигурации были статически созданы служебные
сигналы модуля.
TCP Server
Режим работы активного сервера некорректно определялся модулем HUB после
перезапуска резервной пары серверов.
Модуль истории
После изменения типа сигнала не удавалось получить историю значений и событий из БД
PostgreSQL.
Модуль логики
Устранена «Ошибка записи в параметр <Имя сигнала>. Неверный тип инженерного
значения» при использовании в проекте обработчиков событий.
6.4.18
Улучшение
UNET Client
Реализован новый режим чтения архивных данных C учётом позиции в архиве, который
позволяет избегать повторного чтения уже прочитанных данных.
Исправленная ошибка
UNET Client
Иногда в сигналы могли записываться некорректные значения в режиме чтения Оперативные
данные и использовании версии протокола UNET2.
8
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 261 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
6.4.19
Улучшение
Security Client
Реализована возможность настройки порта подключения к Alpha.Security.
Исправленные ошибки
Модуль истории
Не удавалось получить историю событий и значений из БД Alpha.Historian, если сохранение
истории велось одновременно в БД PostgreSQL и Alpha.Historian, а связь с PostgreSQL
отсутствовала.
TCP Server, Модуль истории, подсистема буферизации
Потребитель не получал последнее значение сигнала, если фильтрация была настроена только
по времени, значение было отброшено фильтром, а нового значения не поступало.
Добавлены доработки Alpha.Server версий 6.3.25, 6.3.26 и 6.3.27
Улучшение
MQTT Client
Реализован новый алгоритм работы очередей приёма и отправки данных.
Исправленные ошибки
OPC AE Server
При квитировании подавленного события информация по квитированию не отображалась в
Alpha.HMI.Alarms.
При получении событий с помощью функции Refresh в оперативных событиях ошибочно
отображались события, сгенерированные по источнику в период подавления.
При подавлении событий по источнику агрегатор не учитывал активацию/деактивацию
событий.
Подсистема резервирования
После переподключения сетевых адаптеров оба сервера резервной пары находились В
работе.
Модуль истории
Сообщение «История событий. Не удалось найти источник события {0}» ошибочно
записывалось в журнал модуля с уровнем Предупреждения и аварийный сообщения. Теперь
данное сообщение записывается только в журнал с уровнем Отладочные сообщения.
Modbus TCP Master
Иногда после перезагрузки ПЛК и получения ошибки 6 (Slave Device Busy) модуль не
возобновлял обмен данными с этим ПЛК.
6.4.20
Улучшение
Механизм фильтрации значений
Изменение CustomInfo теперь учитывается при фильтрации значений аналогично изменению
качества.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
9

=== Page 262 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
6.4.21
Исправленная ошибка
UNET Client
По протоколу UNET2 модуль не записывал в ПЛК значения с протокольным типом без качества.
6.4.22
Улучшение
OPC AE Server
Реализована возможность задержки генерации события. Задержка определяет время, через
которое выполнится генерация события после наступления условия генерации. Если за заданное
время условие генерации исчезнет, то событие не будет сгенерировано.
6.4.23
Улучшение
EtherNet/IP Scanner
Реализовано принудительное обновление метки времени у служебного сигнала «Connected» при
инициации подключения модуля к устройству.
Исправленные ошибки
EtherNet/IP Scanner
После перезапуска модуля служебный сигнал интервала опроса «PollingInterval» вместо того,
чтобы принимать значение, заложенное в конфигурации, сохранял значение, установленное
пользователем.
BACnet Client
Модуль отправлял широковещательные запросы обнаружения устройств на порт 47808, даже
если в конфигурации устройств был указан другой порт, что приводило к невозможности опроса
устройств.
Добавлены доработки Alpha.Server версий 6.3.28 и 6.3.29
Улучшения
Modbus TCP Master
Реализована возможность настройки паузы между запросами.
Siemens S7 Client
Теперь строки любой длины записываются в сигнал с актуальной длиной без усечения на 1
символ.
10
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 263 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Исправленные ошибки
Модуль вычислений
Исправлена ошибка, из-за которой вычисление по формуле могло выполняться по-разному в
ОС AstraLinux и в ОС Windows.
TCP Server
Узел, который является зоной, ошибочно отображался в Alpha.HMI.Alarms не только как
зона, но и как источник.
Siemens S7 Client
В редких случаях модуль переставал получать входящие значения после перезагрузки ПЛК,
а в журнале работы модуля формировалось сообщение об ошибке.
SQL Connector
SQL-запросы не выполнялись после потери и последующего восстановления связи с БД.
Модуль истории
При отсутствии папки для файла очереди и значении параметра Очередь данных:
«Оперативная» – модуль не подключался к БД PostgreSQL;
«Файловая» – модуль не создавал папку для очереди и не информировал об ее
отсутствии в журнале работы модуля и в журнале приложений.
EtherNet/IP Scanner
Исправлена ошибка, из-за которой Alpha.Server мог загружать все ядра процессора на
100%.
6.4.24
Улучшение
IEC-101 Master
Поддержан обмен данными с подчиненными станциями с использованием различных размеров
полей ASDU согласно спецификации. Добавлены возможности:
Определения размеров полей ASDU на станции, проверки соответствия размеров полей и их
значений при обмене данными со станцией.
Указания размера поля адреса ASDU для станции.
Теперь модуль:
Поддерживает работу со станциями, номера которых превышают значение 255.
Использует номера станций 255 и 65535 для отправки широковещательных команд.
Исправленные ошибки
Модуль истории
В OC Linux повышалась загрузка ЦП при использовании функции повторного сохранения
последней записи сигнала в историю.
Служба Alpha.Server зависала в процессе остановки после неудачной попытки запроса истории
в результате потери соединения с БД.
Добавлена доработка Alpha.Server версии 6.3.30
Исправленные ошибки
OPC AE Server
Исправлены ошибки, из-за которых при использовании механизма подавления и блокировок
в оперативном журнале клиентского приложения мог неверно отображаться состав событий
после переподключения.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
11

=== Page 264 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Локализация
Обновлены файлы с текстами интерфейса, которые подлежат переводу на английский язык.
6.4.25
Улучшение
OPC UA Client
В свойства модуля добавлен параметр Присваивать метку времени, который определяет, какую
метку времени модуль будет использовать в качестве метки времени входящих данных:
полученную от источника по подписке сигнала или
сгенерированную сервером в момент получения сигнала.
Исправленные ошибки
Alpha.AccessPoint
Исправлены ошибки, из-за которых в редких случаях могло прекратиться обновление данных, а
возобновить обновление удавалось только перезапуском процесса Alpha.AccessPoint.
OPC UA Client
Исправлены ошибки, из-за которых иногда после разрыва и последующего восстановления
соединения между модулем и OPC UA сервером модуль не получал данные, накопленные OPC UA
сервером за время отсутствия связи.
6.4.26
Улучшение

IEC-104
Реализован общий модуль IEC-104, который объединяет в себе возможности модулей IEC-104
Master и IEC-104 Slave. Общий модуль IEC-104 может работать в трех режимах:
только как IEC-104 Master;
только как IEC-104 Slave;
как IEC-104 Master и IEC-104 Slave одновременно.
6.4.27
Улучшения
Alpha.Server
Теперь при установке компонента на чистую ОС (на которую ранее не устанавливался
Alpha.Server и другие компоненты) идентификатор экземпляра Alpha.Server InstanceId:
Добавляется в *.json-файл параметров экземпляра Alpha.Server, если при установке на
диске не было найдено ни *.json-файла, ни *.xml-файла настройки Alpha.Server.
Не добавляется в *.xml-файл настройки Alpha.Server, даже если он присутствовал на диске
при установке и в нем не был указан InstanceId.
12
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 265 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Siemens S7 Client
В конфигурацию модуля добавлен параметр Устанавливать плохое качество при остановке
устройства, который отвечает за установку значения качества сигналов при остановке ПЛК:
Если параметр выключен, то при остановке ПЛК качество сигналов остается таким, каким
было на момент остановки.
Если параметр включен, то при остановке ПЛК качество сигналов меняется на DEVICE_
FAILURE (12), а после последующей активации ПЛК сначала принимает значение UNCERTAIN
(64), а затем текущее актуальное.
Модуль истории
Добавлены служебные сигналы диагностики соединения модуля с базой данных PostgreSQL:
для оперативной очереди данных:
Наличие связи по каналу
Число записей в очереди
для файловой очереди данных:
Наличие связи по каналу
Число записей в очереди
Число записей в очереди, сохраненных на диск
Текущий размер данных, ожидающих сохранения на диск, Кб
Исправленные ошибки
Alpha.Server
Устранена проблема бинарной несовместимости, из-за которой компонент иногда мог прекратить
работу при запуске.
Для ОС Windows исправлено автоматическое добавление идентификатора экземпляра
Alpha.Server InstanceId в *.xml-файл настройки при обновлении Alpha.Server, что вызывало
необходимость повторно вручную удалять InstanceId из *.xml-файла. Добавление InstanceId в *.xml-
файл при обновлении делало невозможным запуск службы Alpha.Server, так как в это время
использовался InstanceId *.json-файла параметров экземпляра, который создается при
развертывании конфигурации из Alpha.DevStudio.
OPC UA Client
Устранена причина, по которой при обмене данными между модулем и OPC UA сервером через
межсетевой шлюз после потери и последующего восстановления соединения модуль не получал
данные из буфера, накопленные за время отсутствия связи.
Добавлена доработка Alpha.Server версии 6.3.31
Исправленные ошибки
Alpha.Server
Устранены причины, из-за которых компонент прекращал работу, если при обмене данными
между двумя Alpha.Server по протоколу Alpha.Link у модуля HUB одного из них был настроен
удаленный доступ к истории другого.
Изменен внутренний механизм резервного копирования конфигурации Alpha.Server для ОС
Linux, т.к. при прежнем способе в редких случаях резервная копия конфигурации не создавалась,
если папка для резервных копий и исполняемый файл Alpha.Server находились в разных разделах
файловой системы.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
13

=== Page 266 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Alpha.AccessPoint
Устранена причина, из-за которой после перезапуска службы Alpha.Historian:
сигналы для диагностики БД, которые получал Alpha.Server через модуль HUB и которые
участвовали в вычислениях, становились плохого качества COMM_FAILURE (24);
в журнале работы модуля HUB формировались сообщения о том, что качество сигналов
отличается от GOOD (192).
Проблема проявлялась на транзакционной модели исполнения Alpha.Server.
Подсистема резервирования
Устранены причины, из-за которых иногда при частых резервных переходах и включенном
модуле Modbus RTU Master резервный сервер мог прекратить работу.
Modbus TCP Master
Исправлена ошибка, из-за которой при получении ответа на запрос после истечения Времени
ожидания ответа от станции или на запрос, который не отправлялся, модуль разрывал связь по
каналу, при этом не было достигнуто Максимальное количество неуспешных запросов.
6.4.28
Улучшения
SNMP Manager
В рамках одного модуля частично сняты ограничения на прием уведомлений от разных агентов
на одном IP-адресе и на одном порту.
Универсальный модуль для связи с устройствами
Теперь при переходе в режим РЕЗЕРВ модуль может взаимодействовать с устройствами в одном
из трех режимов:
«Закрывать соединение» – модуль закрывает соединения со всеми источниками и по всем
каналам, подключение выполняется только после возврата Alpha.Server в режим РАБОТА;
«Поддерживать соединение» – модуль поддерживает соединения с устройствами, но обмен
данными не выполняется;
«Выполнять получение данных» – модуль продолжает получать данные от устройств, но сам
данные не отправляет.
Data Buffer
В конфигурацию модуля добавлен параметр Перекладывать первое значение, который
позволяет настроить режим обработки того значения, которое первым после начала работы модуля
записывается в сигнал, взятый модулем на обслуживание. Возможные значения параметра:
«false» – первое значение не будет переложено в сигнал объекта-получателя;
«true» – первое значение будет переложено в сигнал объекта-получателя.
Изменения
OPC DA Client
Увеличено максимально допустимое значение частоты опроса OPC DA сервера: теперь можно
задать произвольное целочисленное значение в диапазоне, соответствующем типу UInt32, и оно не
будет усечено.
Исправленные ошибки
Alpha.Server
Исправлена ошибка, из-за которой служба Alpha.Server останавливалась, если в Модуле
логики свойству Вычислять формулы на основании начальных значений было установлено
14
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 267 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
значение «Да».
Устранена причина, по которой компонент мог прекратить работу на ОС Linux при попытке
подключения модуля Security Client к агенту безопасности.
На ОС Linux устранена повышенная загрузка ЦП при работе службы Alpha.Server.
IEC-101 Slave
Устранена причина, по которой на некоторых версиях ОС Linux при опросе подчиненной станции
мастером происходили периодические разрывы связи с последующим восстановлением
соединения.
IEC-104
Исправлена ошибка, из-за которой модуль не отправлял на станцию команды с
предварительным выбором значения.
Modbus TCP Master
Исправлена ошибка, из-за которой при работе в резерве в режиме «Поддерживать соединение»
модуль продолжал вести опрос устройств.
Общее для всех модулей, использующих TCP:
Исправлена ситуация, когда в некоторых случаях на Linux-системах потеря связи по TCP-
соединению своевременно не детектировалась.
Добавлена доработка Alpha.Server версии 6.3.32
Изменение
OPC UA Client
Количество OPC UA серверов, к которым может единовременно подключиться OPC UA Client
одного экземпляра Alpha.Server, увеличено со 100 до 200.
Добавлена доработка Alpha.Server версии 6.3.33
Исправленные ошибки
OPC AE Server
Исправлена работа агрегатора событий - параметры агрегации количество активных событий и
максимальная важность среди активных событий неверно подсчитывались при:
квитировании активного события;
квитировании неактивного события, которое было сгенерировано до подавления источника.
Устранена причина, из-за которой модуль отправлял клиентам оперативные уведомления о
событиях от подавленных источников, при этом обработка подавленных событий выполнялась на
стороне сервера.
Подсистема резервирования
Исправлена ошибка, из-за которой иногда после старта резервной пары сигналы могли не
реплицироваться на резервный сервер.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
15

=== Page 268 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Изменения документации
Редакция 1
Модуль истории. Руководство администратора
Обновлена структура и содержимое документации:
В разделе "Назначение и принципы работы" (стр. 5):
В перечне функций модуля добавлены БД, в которые модуль сохраняет события, и из
которых запрашивает данные.
В пункте "Сохранение данных" обновлен рисунок и добавлен блок "Обратите внимание"
(стр. 5).
В пункте "Запрос сохранённых данных" обновлен рисунок и добавлен блок "Обратите
внимание" (стр. 6).
Добавлено описание настройки модуля в Alpha.DevStudio (стр. 8).
Добавлена глава "Периодическое повторное сохранение последней записи сигнала" (стр. 25).
Добавлена глава "Сохранение дополнительной метки времени сервера" (стр. 26).
В приложении "Установка и настройка PostgreSQL" (стр. 40):
В разделе "ОС Windows" обновлён пункт 2.3 (стр. 42), добавлены пункты 2.4-2.6 (стр. 44).
В разделе "ОС Linux" обновлён пункт 8 (стр. 46).
Добавлен подраздел "Установка и настройка драйвера ODBC" (стр. 47).
Добавлена глава "Ускорение получения истории значений из БД PostgreSQL" (стр. 48).
Добавлено описание установки и настройки MS SQL Server (стр. 50).
Описание настройки в Конфигураторе перенесено в приложение (стр. 55)
Модуль OPC HDA Client. Руководство администратора
В раздел "Параметры статистики" добавлены подразделы с описанием параметров статистики
модуля, группы серверов, сервера (стр. 8).
Обновлена информация в разделе "Журнал работы модуля" (стр. 10).
Модуль OPC DA Client. Руководство администратора
В разделе "Параметры статистики" (стр. 17):
обновлены картинки;
добавлено описание параметров Количество опрашиваемых свойств и Размер очереди
входящих данных.
Обновлена информация в разделе "Журнал работы модуля" (стр. 20).
Модуль логики. Руководство администратора
Добавлена глава "Статистика модуля" (стр. 32).
16
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 269 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Модуль Modbus TCP Master. Руководство администратора
В разделе "Служебные сигналы" добавлено описание служебных сигналов (стр. 28):
контроля состояния источника;
опроса категорий данных по команде;
контроля и управления станцией;
контроля и управления каналами станции;
контроля и управления основными параметрами модуля.
В разделе "Параметры статистики" (стр. 32):
обновлены картинки;
добавлено описание:
параметра станции Состояние;
параметров источника Состояние и Размер очереди команд;
параметров категории данных Среднее время опроса, мс и Количество сигналов.
Обновлена информация в разделе "Журнал работы модуля" (стр. 38).
Модуль IEC-61850 Client. Руководство администратора
В раздел "Параметры статистики" добавлены подразделы с описанием параметров статистики
модуля, устройства, каналов, данных поллинга, исходящих данных, блоков отчётов, файлового
обмена (стр. 34).
Обновлена информация в разделе "Журнал работы модуля" (стр. 38).
Модуль BACnet Client. Руководство администратора
В раздел "Параметры статистики" добавлены подразделы с описанием параметров статистики
модуля, источника, устройства, канала, локальных интерфейсов (стр. 36).
Модуль TCP Server. Руководство администратора
Обновлены рисунки.
В разделе "Добавление TCP клиента" обновлен пункт 1 (стр. 7, 8).
Редакция 2
Модуль OPC AE Server. Руководство администратора
Обновлена структура и содержимое документации:
В разделе "Функциональные возможности" (стр. 7):
Обновлено описание функциональных возможностей модуля (стр. 7).
Обновлено и выделено в отдельную главу описание генерации событий (стр. 7).
Добавлена глава "Пользовательские атрибуты событий" (стр. 25).
Добавлена глава "Внешние события" (стр. 26).
Обновлено и выделено в отдельную главу описание квитирования (стр. 28).
Обновлено и выделено в отдельную главу описание блокирования и подавления событий
(стр. 29).
Обновлено и выделено в отдельную главу описание работы модуля в резерве (стр. 31).
Добавлено описание настройки модуля в Alpha.DevStudio (стр. 32).
Описание настройки в Конфигураторе перенесено в приложение (стр. 54).
Добавлен раздел "Оперативная таблица событий (ОАТ)" (стр. 36).
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
17

=== Page 270 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
В разделе "Агрегация событий" (стр. 39):
Обновлено описание агрегации событий.
Исключена глава "Настройка агрегации событий по ветке".
Исключена глава "Настройка фильтров агрегаторов".
Исключена глава "Работа агрегаторов со ссылками".
Исключен раздел "Описание файла конфигурации сервера".
Исключен раздел "Пример работы с модулем".
Модуль SnapShot. Руководство администратора
Обновлена структура и содержимое документации:
Обновлен раздел "Назначение и принцип работы" (стр. 4).
В разделе "Настройка модуля" добавлено описание настройки в Alpha.DevStudio. (стр. 5).
Обновлен раздел "Служебные сигналы модуля" (стр. 8).
В разделе "Запись данных в файл-срез" обновлено описание и добавлены главы (стр. 14):
"Запись данных в файл-срез исходного формата" (стр. 15).
"Запись данных в файл-срез стороннего формата" (стр. 16).
"Результат генерации" (стр. 18).
"Сообщения об ошибках" (стр. 18).
"Генерация файла-среза при остановке модуля" (стр. 18).
Обновлен раздел "Формат шаблона файла-среза" (стр. 21).
Обновлен раздел "Формат файла-среза" (стр. 25).
Раздел "Работа с массивом файлов-срезов" переименован в "Просмотр массива файлов-
срезов" и обновлен (стр. 30).
Обновлен раздел "Восстановление данных из файла-среза" (стр. 34).
Обновлен раздел "Диагностика работы модуля" (стр. 37).
Описание настройки модуля в Конфигураторе исключено.
Alpha.Imitator. Руководство администратора
В главу "Дополнение пропущенных исторических данных" добавлен блок "Обратите внимание" с
информацией о формате файлов данных и их расположении (стр. 55).
Модуль OPC UA Client. Руководство администратора
Добавлены примечания о возможности работы модуля с разными группами серверов в разном
Режиме работы в РЕЗЕРВЕ одновременно для настройки модуля в Alpha.DevStudio и Конфигураторе
(стр. 22, 34).
Модули NetDiag, NetDiag2. Руководство администратора
Добавлено описание настройки запуска модуля NetDiag2 от имени непривилегированного
пользователя в ОС Linux (стр. 15).
Модуль истории. Руководство администратора
В главу "Добавление сервера истории и настройка БД" в пункте для Alpha.Historian в блоке
"Обратите внимание" добавлен отсутствующий блок кода (стр. 10).
Исправлены неработающие ссылки.
Редакция 3
Добавлена документация для Универсального модуля для связи с устройствами (Универсальный
модуль для связи с устройствами. Руководство администратора).
18
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 271 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Модуль OPC AE Server. Руководство администратора
В главе "Генерация событий" в описание типа условия "Динамическое":
Добавлен алгоритм создания динамических событий (стр. 10).
Расширен перечень возможных источников для генерации динамических событий (стр. 10).
В раздел "Блокирование и подавление" добавлены сведения об ограничении правил обработки
подавленных событий для клиентов (стр. 29).
Раздел "Работа модуля в резерве" актуализирован и дополнен описанием отличий работы в
разных моделях исполнения сервера (стр. 30).
В главе "Оперативная таблица событий (OAT)" добавлено:
Подраздел "OAT в режиме резервирования" (стр. 39).
Примечание о том, что в OAT не сохраняются события по блокированным и подавленным
источникам (стр. 37).
В главу "Агрегация событий" добавлены сведения о новых параметрах агрегации: минимальной
важности среди активных событий и минимальной важности среди неквитированных событий (стр.
40).
Модуль SnapShot. Руководство администратора
В раздел "Запись данных в файл-срез" добавлена глава "Запись в файл-срез по индексам
сигналов" (стр. 19).
Модуль DTS Client. Руководство администратора
Добавлено описание настройки модуля в Alpha.DevStudio (стр. 7).
Обновлены схемы.
Модуль BACnet Client. Руководство администратора
Обновлено описание служебных сигналов модуля (стр. 35).
Редакция 4
MQTT ClientМодуль MQTT Client. Руководство администратора
Добавлена документация для модуля MQTT Client.
КонфигураторСервисное приложение Конфигуратор. Руководство администратора
Добавлена глава "Ресурсы Alpha.Server" (стр. 17).
Редакция 5
Модуль Security Client. Руководство администратора
Добавлена документация для модуля Security Client.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
19

=== Page 272 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Модуль SNMP Manager. Руководство администратора
Обновлена структура и содержимое документации:
Обновлен раздел "Назначение и принцип работы" (стр. 4).
Раздел "Безопасность в протоколе SNMPv3" переименован в "Безопасность в протоколах
SNMP" и дополнен (стр. 6).
Обновлены и выделены в отдельный раздел сведения о преобразовании типов данных и
качестве сигналов (стр. 7).
Обновлен раздел "Способы получения данных от агентов" (стр. 8).
Добавлено описание настройки обмена данными между модулем и агентом в
Alpha.DevStudio (стр. 11).
Обновлен раздел "Диагностика работы" (стр. 24).
Описание настройки обмена данными в Конфигураторе обновлено и перенесено в
Приложение (стр. 29).
Модуль FINS Client. Руководство администратора
В главе "Настройка FINS Client" (стр. 13):
Обновлена картинка и описание свойств Клиента FINS.
Добавлен блок "Обратите внимание" с информацией о настройке параллельного опроса
одного ПЛК серверами резервной пары.
Модуль истории. Руководство администратора
Добавлено описание таблиц, добавляемых в БД PostgreSQL при выполнении скрипта
postgresql.9.5.sql (стр. 48).
Редакция 6
Модуль SQL Connector. Руководство администратора
Обновлена информация о совместимости модуля с версиями СУБД PostgreSQL и Postgres Pro
Standard (стр. 5).
Модуль истории. Руководство администратора
Обновлена информация о совместимости модуля с версиями СУБД PostgreSQL и Postgres Pro
Standard (стр. 5).
Уточнена возможность фильтрации значений сигналов в описании дополнительных параметров
сохранения истории (стр. 23).
В разделе Диагностика работы при упоминании подключения модуля к БД Alpha.Historian
исправлен способ подключения с OPC на DCOM, а способ подключения по TCP обозначен как
рекомендуемый (стр. 29).
20
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 273 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Модуль OPC UA Server. Руководство администратора
Обновлены параметры аутентификации в описании настройки обмена данными с OPC UA
клиентом в среде разработки Alpha.DevStudio и в сервисном приложении Конфигуратор (стр. 5).
Обновлен раздел "Способы аутентификации" (стр. 20).
Раздел "Работа с клиентскими сертификатами" переименован в "Сертификаты", дополнен
сведениями о хранилище сертификатов и видах сертификатов (самоподписанные и подписанные
центром сертификации), а также подразделами (стр. 24):
Сертификат модуля с описанием создания и продления сертификата модуля OPC UA Server
(стр. 25).
Клиентские сертификаты с описанием требований к клиентским сертификатам (стр. 30).
Управление сертификатами (стр. 31).
Добавлено приложение "Параметры спецификации OPC UA", в котором приведено соответствие
свойств модуля OPC UA Server стандартным параметрам спецификации OPC UA (стр. 48).
Модуль OPC UA Client. Руководство администратора
Обновлено описание настроек параметров безопасности в разделе настройки обмена данными с
OPC UA клиентом в среде разработки Alpha.DevStudio и в сервисном приложении Конфигуратор
(стр. 6).
Раздел "Аутентификация в режиме Сертификат" обновлен и объединен с разделом "Установка
безопасного соединения" (стр. 48).
Добавлен подраздел Сертификат модуля с описанием создания и продления сертификата
модуля OPC UA Client (стр. 51).
Добавлено приложение "Параметры спецификации OPC UA", в котором приведено соответствие
свойств модуля OPC UA Client стандартным параметрам спецификации OPC UA (стр. 64).
Подсистема резервирования. Руководство администратора
Обновлен состав и описание служебных сигналов (стр. 17).
Редакция 7
Модуль TCP Server. Руководство администратора
Обновлен раздел "Настройка обмена данными с TCP клиентом":
Подраздел "Добавление TCP клиента" дополнен сведениями об элементе Потребитель Link
(стр. 7).
Добавлен пункт "Разрешение изменения значений сигналов только для
аутентифицированных клиентов" (стр. 14).
Модуль OPC AE Server. Руководство администратора
Исправлена опечатка в пункте "Ручная очистка" подраздела "Оперативная таблица событий
(OAT)" (стр. 38).
Модуль MQTT Client. Руководство администратора
В разделе "Туннелирование через MQTT" добавлен блок "Обратите внимание" (стр. 36).
Модуль Siemens S7 Client. Руководство администратора
Обновлен раздел "Настройка в Alpha.DevStudio": актуализированы свойства и параметры,
обновлены изображения (стр. 9).
Исключено описание настройки обмена данными с ПЛК в Конфигураторе.
Модуль EtherNet/IP Scanner. Руководство администратора
В раздел "Настройка модуля" добавлено описание параметра Метрика (стр. 9).
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
21

=== Page 274 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Модуль истории. Руководство администратора
В Приложении "Установка и настройка PostgreSQL" приведены возможные значения столбцов
таблицы EventHistory и дано их описание (стр. 50).
Модуль Security Client. Руководство администратора
Раздел "Получение значений из Alpha.Security" дополнен сведениями о пользователе по
умолчанию, от имени которого выполняются настройки получения значений параметров из
Alpha.Security (стр. 6).
6.3
В Alpha.Server 6.3.0 добавлена функциональность Alpha.Server версий 6.0.15 - 6.0.27, 6.1.0 - 6.1.5, 6.2.0.
ОБРАТИТЕ ВНИМАНИЕ
Конфигурирование Alpha.Server для использования новых возможностей и улучшений возможно
только в Alpha.DevStudio 3.27.0.
Новые возможности
IEC-104 Master
Работа с несколькими станциями с одинаковым номером по разным каналам.
Возможность указывать параметры взаимодействия со слэйвом для каждой станции
(источника).
Использование метки времени сервера при настройке протокольного типа без метки времени.
ОБРАТИТЕ ВНИМАНИЕ
Изменилась структура конфигурации модуля (в том числе состав полей адресного свойства) и
структура служебных сигналов модуля.
IEC-104 Slave
Возможность использовать разный общий адрес ASDU в рамках одного источника.
Возможность указывать параметры взаимодействия с потребителем для каждой станции
(источника).
Поддержка механизма команд с предварительным выбором с возможностью внешней и
внутренней блокировки управления.
Настройка передачи служебных команд в соответствии со спецификацией протокола IEC:
Отправка пакета с причиной передачи 10 (завершение активации) в направлении контроля.
Отправка типа данных 70 (конец инициализации) с причиной передачи 4 (сообщение об
инициализации) в направлении контроля.
Приём команд с предварительным выбором.
ОБРАТИТЕ ВНИМАНИЕ
Изменилась структура конфигурации модуля (в том числе состав полей адресного свойства) и
структура служебных сигналов модуля.
IEC-104 Master, IEC-104 Slave
При отправке/получении данных по протоколу МЭК добавлена возможность обработки (на
приём) и формирования (на отправку) качества МЭК. Конвертация качества выполняется с помощью
библиотеки, разработанной с учётом нужной логики конвертации, с возможностью использования (на
отправку) или задания (на приём): OPC качества, CustomInfo и адреса сигнала.
22
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 275 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
OPC UA Server, OPC UA Client
При отправке/получении данных по спецификации OPC UA добавлена возможность обработки
(на приём) и формирования (на отправку) качества OPC. Конвертация качества выполняется с
помощью библиотеки, разработанной с учётом нужной логики конвертации, с возможностью
использования (на отправку) или задания (на приём): OPC качества, CustomInfo и адреса сигнала.
Modbus TCP Master
Адресация данных, обмен которыми выполняется по конкретному устройству в источнике.
Определение контрольного узла на устройстве, по значению которого определяется готовность
устройства к работе.
Определение возможности использования устройств в источнике и каналов в устройстве при
старте модуля.
Модуль логики
Вызов внешних функций с прореживанием данных: если предыдущий вызов функции еще не
начал выполняться, то новый вызов замещает его в очереди на исполнение. Прореживание данных
позволяет уменьшить задержку обработки очереди задач функциями из внешних библиотек,
которые могут потенциально выполняться долго.
OPC AE Server
Квитирование событий с ограничением по времени. Для активных событий сигнализация
срабатывает повторно через заданный промежуток времени.
OPC DA Server
Чтение отдельных атрибутов сигналов стороннего OPC DA сервера.
IEC-101 Master
Файловый обмен с устройством.
EtherNet/IP Scanner
Отключение устройства и выбор активного устройства с помощью служебных сигналов.
Изменение периода опроса группы с помощью служебного сигнала «PollingInterval.Set».
IEC-61850 Client
Получение от устройств IEC 61850 структурных типов данных.
Улучшения
Модуль логики
Повышена информативность сообщения об исключении при выполнении функции динамической
библиотеки. Теперь при возникновении исключения сообщение содержит:
имя обработчика, вызвавшего функцию;
имя функции, указанное пользователем;
имя библиотеки, указанное пользователем;
код исключения.
OPC UA Server, OPC UA Client
Поддержана конвертация качества значения сигнала в StatusCode согласно спецификации OPC
UA.
IEC-104 Master
Реализовано логирование ошибок валидации данных по текущему алгоритму. В сообщении
указывается метка времени данных, которая получена от устройства, и причина ошибки.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
23

=== Page 276 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
BACnet Client
Возможность взаимодействия со шлюзом, который использует широковещательный адрес
(«255.255.255.255») для отправки ответов на запросы.
В журнале модуля:
область расшифровки кадров содержит информацию о свойствах, на которые
создаётся/отменяется подписка, а также значения свойств, получаемые по подписке;
для всех входящих/исходящих кадров содержится название службы, которая была
использована во входящем/исходящем запросе.
Текст сообщений в журнале приложений содержит расшифрованный код ошибки разбора JSON-
строк.
Добавлен служебный сигнал «SetSubscription» для управления подпиской по Area или подписки
на любые свойства модуля.
Исправленные ошибки
Alpha.Server
Устранены редкие причины прекращения работы Alpha.Server при резервном переходе,
выполнении вычислений.
Alpha.Imitator
Alpha.Imitator завершал работу при попытке ввода некорректного значения в служебный сигнал
«Service.Imitation.Override».
Было невозможно прервать сессию имитации до окончания загрузки данных. Теперь прервать
сессию можно в любой момент, установив служебному сигналу «Service.Imitation.EndSession»
значение «True».
Команда Update ошибочно добавляла записи в новый набор данных при отсутствии записи с
меткой времени, указанной в параметрах команды.
Для тега, в имени которого присутствовали символы кириллицы:
не запрашивалась история значений через служебный сигнал
«Service.Imitation.ReadHistory»;
не перезаписывалась история значений через служебный сигнал
«Service.Imitation.Override».
При вводе некорректной JSON-строки в служебные сигналы «ReadHistory», «Override» и
«ReadOverriden» в журнал приложений записывалось неинформативное сообщение. Теперь текст
сообщения содержит имя служебного сигнала и описание ошибки.
Alpha.AccessPoint
Устранена запись сообщения вида «GetSignalHandle: Нельзя добавить в список сигналов
папку <имя_сигнала>» в журнал приложений для модуля TCP Server при попытке на экране
Alpha.HMI использовать папки.
В некоторых случаях в журнал модуля HUB ошибочно записывалось сообщение о совпадении
идентификаторов источников.
Конфигуратор, Статистика
Исправлены опечатки в названии параметра статистики модуля HUB.
При просмотре списка устройств IEC-61850 Client имена устройств с дефисом ошибочно
отображались без дефиса.
24
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 277 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Дистрибутив
В ОС Linux установленные на одном компьютере Alpha.Server и Alpha.AccessPoint сохраняли
журналы работы модулей и резервные копии конфигураций в общие для них каталоги
/opt/Automiq/Logs и /opt/Automiq/Backups. Теперь журналы работы модулей и резервные копии
конфигураций сохраняются в каталоге установки компонента:
Alpha.Server - /opt/Automiq/Alpha.Server/Logs и /opt/Automiq/Alpha.Server/Backups
Alpha.AccessPoint - /opt/Automiq/Alpha.AccessPoint/Logs и
/opt/Automiq/Alpha.AccessPoint/Backups
Модуль истории
Подключение к БД становилось невозможным после неуспешных попыток установления
соединения с хранилищем Postgre.
Просмотрщик лога кадров
В очень редких случаях в ОС Linux могли повреждаться журналы работы модулей Alpha.Server.
При открытии такие журналы не содержали записей.
OPC AE Server
Агрегатор не применял фильтр «Кроме указанных важностей событий» и включал в результат
агрегации события, которые не должны были учитываться.
При получении событий с помощью функции Refresh:
не обрабатывалась процедура, выполняемая при генерации события;
текст сообщения в клиенте не заменялся на текст, заданный пользователем;
возвращалось событие со старым значением важности вместо измененного.
IEC-101 Master
Второй канал не мог быть использован станцией как основной при отключенном резервировании
канала для станции.
IEC-101 Slave
Устранены многочисленные сообщения об ошибке конвертации качества в журнале приложений
при отправке качества, значение которого лежит за границей допустимых значений. Теперь в журнал
записывается только одно сообщение об ошибке конвертации качества.
SNMP Manager
При использовании протокола SNMPv3 модуль мог ошибочно выбирать активным канал, по
которому не установлена связь с агентом.
IEC-104 Master
Устранены многочисленные сообщения в журнале приложений об обработке очереди входящих
данных.
IEC-104 Slave
При одновременном получении нескольких команд модуль мог отправлять в ответ кадры
подтверждения или завершения активации дважды по одному и тому же адресу.
IEC-61850 Client
Иногда при большом количестве устройств смена режима работы Alpha.Server могла
происходить долго.
Не загружались файлы с устройства IEC 618506:
из-за отличия размера файла от ожидаемого;
модуль не находил папку для приёма файлов.
OPC UA Server
При усечении значения по границе пересчета сигналу устанавливалось качество BAD вместо
SENSOR_FAILURE.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
25

=== Page 278 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Изменения
OPC UA Server
Параметр Аутентификация учетной записью Windows переименован в Аутентификация учетной
записью ОС.
Сервисные приложения
Новые иконки сервисных приложений Конфигуратор, Статистика, Управляющий.
6.3.1
В Alpha.Server 6.3.1 добавлена функциональность Alpha.Server версий 6.2.1 - 6.2.4.
Улучшение
Модуль логики
Реализована возможность при запуске Alpha.Server вычислять значения всех формул на
основании начальных значений переменных.
Исправленная ошибка
OPC UA Server
Некоторые клиенты не получали данные Alpha.Server.
6.3.2
Новые возможности
FINS Client
Возможность прекращения опроса ПЛК при переходе модуля в резерв.
IEC-104 Master
Возможность использования отдельного TCP-подключения для устройства.
Modbus TCP Master
Возможность адресации к конкретному устройству источника для исходящих сигналов.
26
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 279 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
EtherNet/IP Scanner
Реализован механизм состояний каналов:
Поддержаны состояния каналов:
Connected - наличие соединения по каналу;
Enabled - доступность канала.
Возможность отслеживания и управления состоянием каналов в режиме реального времени с
помощью служебных сигналов.
Реализован механизм состояний устройств:
Поддержаны состояния устройств:
Enabled - доступность устройства;
Connected - наличие соединения с устройством;
Active - активность устройства.
Возможность отслеживания и управления состоянием устройств в режиме реального
времени с помощью служебных сигналов.
Для устройств доступен выбор исходного состояния возможности использования устройства
при старте модуля.
Возможность автоматической генерации имён устройств и каналов модуля.
Возможность указывать период времени, по истечение которого связь с устройством считается
потерянной.
Улучшения
IEC-104 Master
Выполнение проверки источников на наличие станций с одинаковыми настройками. При
обнаружении у разных источников станций с одинаковыми номером, IP-адресом и портом, в журнал
выводится ошибка, а получение данных выполняется по первому обнаруженному источнику.
Модуль резервирования
Добавлены служебные сигналы, отображающие текущее состояние парного сервера в резервной
паре.
EtherNet/IP Scanner
Добавлены служебные сигналы, отображающие IP-адрес и порт канала.
Исправленные ошибки
TCP Server
Известные клиенты, несмотря на запрет, ошибочно могли изменять значения сигналов.
OPC AE Server
В Alpha.HMI.Alarms из OAT помимо активных событий загружались и неактивные с пустым
столбцом Сообщение.
Siemens S7 Client
Связь с ПЛК могла восcтанавливаться долго при нестабильном соединении.
EtherNet/IP Scanner
Качество сигналов ошибочно оставалось хорошим при разрыве связи с резервным сервером и
ПЛК.
Модуль не восстанавливал соединение по каналу, который до разрыва соединения был
неактивным.
Не выполнялась проверка корректности имени канала при загрузке конфигурации из файла
*.xmlcfg.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
27

=== Page 280 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
6.3.3
Улучшение
TCP Server
Запрет на запись анонимным клиентам модуля теперь установлен по умолчанию.
6.3.4
Исправленные ошибки
OPC UA Client
Alpha.Server завершал работу при попытке подключения к UA серверу Орион Про.
Модуль логики
Не генерировалось сообщение о событии при использовании с обработчиком триггера подготовки
сообщения.
Модуль истории
Находясь в резерве модуль сохранял в историю:
первое сгенерированное событие по подусловию;
события не требующие квитирования.
Modbus TCP Master
Исправлены ошибки модуля Modbus TCP Master, из-за которых:
в транзакционной модели исполнения Alpha.Server мог завершать работу;
оба сервера резервной пары запускались в состоянии Активный.
Модуль резервирования
В транзакционной модели исполнения после перезапуска одного из серверов резервной пары оба
сервера переходили в состояние Активный В работе.
Один из серверов резервной пары мог зависать при инициализации.
6.3.5
Улучшения
Модуль логики
Реализована возможность изменения звука перед отправкой события. Для изменения звука в
свойстве сигнала 777013 атрибуту me.Messages.Selected.Sound укажите имя звукового файла.
IEC-104 Slave
Добавлен служебный сигнал «ConnectedCount», отображающий количество подключений к
группе станций («Service.Modules.Iec104Slave.Groups.StationGroup_<номер>.ConnectedCount»).
Исправленная ошибка
OPC AE Server
Устранена запись в журнал приложений сообщений вида "Экземпляр описан вне объекта
'<идентификатор>'" при инициализации модуля.
Добавлены доработки Alpha.Server версий 6.2.6, 5.13.10, 5.13.11.
Улучшение
Уменьшено потребление оперативной памяти модулем логики.
28
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 281 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Исправленные ошибки
Иногда Alpha.Imitator не восстанавливал историю значений некоторых сигналов в режиме
"Дополнение пропущенных исторических данных" (Backfilling).
Иногда обмен данными модуля OPC UA Client с ПЛК мог прекращаться.
6.3.6
Исправленные ошибки
Modbus TCP Master
Устранена проблема, из-за которой один из Alpha.Server резервной пары мог прекращать
работу.
IEC-104 Slave
Устранена проблема, из-за которой Alpha.Server мог прекращать работу при перезапуске.
Modbus TCP Slave
В ОС Linux в транзакционной модели исполнения Alpha.Server мог прекращать работу после
длительного бездействия.
IEC-104 Master
В некоторых случаях при подаче команды с использованием предварительного выбора модуль
мог ошибочно отправлять команду многократно.
6.3.7
Исправленная ошибка
Модуль резервирования
Порт модуля резервирования мог оставаться занятым после перезапуска Alpha.Server, из-за
чего не удавалось установить соединение с резервным сервером.
6.3.8
Новая возможность
Реализован новый модуль MQTT Client, с помощью которого Alpha.Server может обмениваться
данными с устройствами по протоколу MQTT.
6.3.9
Улучшение
FINS Client
Реализована возможность параллельного опроса одного ПЛК OMRON обоими Alpha.Server
резервной пары. Для этого в настройках модуля нужно указать разные адреса узлов источника (SA1)
для основного и резервного серверов.
6.3.10
Исправленные ошибки
SQL Connector
Запрос мог выполнялся чаще, чем было задано в параметре Период исполнения запроса.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
29

=== Page 282 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Modbus TCP Master
Не удавалось опросить несколько станций при одновременной отправке кадров по одному каналу
через шлюз.
6.3.11
Улучшение
IEC-104 Master
Добавлена настройка режима работы резервных каналов, который определяет каким образом
будут использоваться определённые для станции каналы связи.
6.3.12
Улучшение
OPC AE Server
Для подусловия генерации событий добавлена возможность настройки повторной генерации
события по активному подусловию.
Исправленные ошибки
FINS Client
Не выполнялся обмен данными с некоторыми моделями ПЛК OMRON.
OPC AE Server
Важность события не изменялась с помощью вычислений.
Modbus RTU Master
Устранена запись в журнал приложений сообщений вида "В таблице опроса отсутствуют запросы
для подключения".
6.3.13
Улучшения
SNMP Manager
Для агента добавлена возможность использования контекста для разграничения доступа к
нескольким физическим/логическим устройствам.
Добавлена возможность сбрасывать сохраненное время агента при потери связи. Используется
для агентов, неправильно считающих перезагрузки.
Исправленные ошибки
Модуль истории, TCP Server, Модуль логики
Устранены проблемы, из-за которых в редких случаях Alpha.Server мог прекращать работу.
OPC UA Client
В режиме работы в резерве «Закрывать соединение» после двойного резервного перехода
модуль переставал передавать данные на UA Server.
Modbus TCP Master
Для сигналов типа String не учитывалось значение параметра Байт в слове.
30
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 283 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Модуль логики
Устранена ошибка модуля логики "Не найден зарегистрированный член типа" при использовании
в проекте логических типов.
6.3.14
Исправленные ошибки
Модуль истории
Иногда Alpha.Server мог завершать работу при остановке модуля истории.
Устранена причина нарушения целостности OAT.
OPC AE Server
Повторно генерировались события по подусловию Enumeration при резервном переходе.
Генерировалось событие по подусловию Deviation при отсутствии предыдущего значения
сигнала.
OPC UA Client
В режиме работы в резерве «Закрывать соединение» после двойного резервного перехода
модуль переставал получать данные с UA Server.
6.3.15
ОБРАТИТЕ ВНИМАНИЕ
Пользователям Alpha.Server версии 6.3.0 и выше, использующим в конфигурации модуль OPC UA
Client, рекомендуем безотлагательно произвести обновление до версии 6.3.15 для исключения
возможной отправки модулем OPC UA Client, находящимся в резерве, команд в UA Server.
Подробности возможного возникновения проблемы на Alpha.Server версии 6.3.0 и выше смотрите в
разделе "Исправленные ошибки" модуля OPC UA Client настоящей новости.
Улучшение
EtherNet/IP Scanner
Реализована возможность настройки таймаута ожидания ответа на запрос.
Исправленные ошибки
OPC UA Client
Находясь в резерве, модуль отправлял в UA Server уже отправленные ранее команды, получив
их по каналу репликации от основного Alpha.Server после перезапуска Alpha.Server, в составе
которого он функционирует:
В транзакционной модели исполнения модуль отправлял такие команды только для
нереплицируемых сигналов.
В модели исполнения по умолчанию модуль отправлял такие команды как для
реплицируемых сигналов, так и для нереплицируемых.
Дополнительным условием отправки таких команд являлось значение «Запрашивать данные»,
установленное для режима работы модуля в резерве.
TCP Server, HUB
Устранены причины, из-за которых обмен данными между Alpha.Server и Alpha.AccessPoint мог
выполняться некорректно.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
31

=== Page 284 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
6.3.16
Улучшения
OPC AE Server
Добавлены новые агрегаторы:
MinSeverity - минимальная важность среди активных событий;
MinSeverityUnacked - минимальная важность среди активных неквитированных событий.
IEC-104 Master
Добавлена возможность указывать необходимость отправки команды общего опроса при
установке связи по каналу.
IEC-101 Master
Добавлен служебный сигнал «Connected», отображающий состояние связи со станцией.
Добавлена возможность отправки команды синхронизации времени при установлении
соединения со станцией.
Исправленные ошибки
IEC-61850 Client
Устранены проблемы модуля, из-за которых Alpha.Server мог:
потреблять 100% CPU после запуска;
завершать работу при разрыве соединения с устройством.
OPC AE Server
Не генерировались события по условию Deviation при резервном переходе.
6.3.17
Исправленная ошибка
Modbus TCP Master
Иногда модуль мог не опрашивать некоторые станции.
6.3.18
Исправленные ошибки
Alpha.Server
Иногда процесс Alpha.Server мог загружать все ядра процессора на 100%.
Модуль истории
В OC Linux Alpha.Server мог завершать работу после высокой загрузки ЦП при использовании
функции повторного сохранения последней записи сигнала в историю.
IEC-104 Master
Модуль не учитывал, что при общем опросе значения типа <235> M_ME_TX_1 приходят в виде
значений типа <234> M_ME_NX_1, и игнорировал такие значения.
EtherNet/IP Scanner
В OC Linux модуль не устанавливал соединение с устройством.
32
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 285 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
6.3.19
Исправленные ошибки
Modbus TCP Master
При задержке отправки пакетов модуль мог не опрашивать некоторые источники.
Для сервера В резерве устранена запись в журнал работы модуля сообщений вида "Значение
сигнала <Имя сигнала> не было отправлено. Причина: плохое качество (24)".
IEC-104 Master
Модуль не инициализировался при отсутствии в конфигурации значения параметра
SendCommonPollAfterConnect (Отправлять общий опрос при подключении).
OPC AE Server
После запуска сервера ошибочно подавалась команда очистки таблицы оперативных событий.
6.3.20
Исправленные ошибки
OPC AE Server
Устранена ошибка при синхронизации подавлений и блокировок между серверами резервной
пары, из-за которой после резервного перехода могли генерироваться события по подавленным
источникам.
При использовании OAT ошибочно не учитывался признак подавления источников, из-за чего
после переподключения в Alpha.HMI.Alarms могли отображаться события по подавленным
источникам.
6.3.21
Исправленная ошибка
SNMP Manager
Сигналам могло кратковременно устанавливаться плохое качество при повторной смене канала
соединения с агентом.
6.3.22
Улучшение
IEC-104 Master
Реализован новый алгоритм работы очереди входящих данных.
Исправленные ошибки
EtherNet/IP Scanner
Alpha.Server завершал работу при разрыве связи с эмулятором.
IEC-104 Master
Модуль не устанавливал плохое качество сигналам при разрыве связи со станцией в режиме
Один в работе, не поддерживать соединение по остальным.
При возникновении ошибок протокола модуль не разрывал соединение и продолжал работу по
тому же каналу, но записывал сообщения о разрыве соединения в журнал работы модуля. Теперь
при ошибках протокола модуль разрывает соединение, открывает его заново и продолжает работу.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
33

=== Page 286 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Modbus RTU Slave, Modbus TCP Slave
Модули ошибочно добавляли в конец строки символ '\0' в кодировках utf8 и windows-1251, если
длина строки была нечетным числом.
Siemens S7 Client
При получении строки с ПЛК значение в Alpha.Server могло быть некорректным.
Alpha.Server
Устранены ошибки, возникавшие при использовании в вычислениях элементов массива.
6.3.23
Новая возможность
Реализован новый модуль GenericDeviceComm, с помощью которого Alpha.Server может
обмениваться данными с устройствами по DCON.
Исправленные ошибки
OPC AE Server, Модуль логики
Исправлены ошибки, из-за которых в некоторых случаях могли прекращаться генерация
событий и выполнение вычислений, а Alpha.Server мог завершать работу или зависать при
остановке.
6.3.24
Исправленные ошибки
EtherNet/IP Scanner
Модуль не инициализировался, если в конфигурации были статически созданы служебные
сигналы модуля.
TCP Server
Режим работы активного сервера некорректно определялся модулем HUB после перезапуска
резервной пары серверов.
Модуль истории
После изменения типа сигнала не удавалось получить историю значений и событий из БД
PostgreSQL.
Модуль логики
Устранена «Ошибка записи в параметр <Имя сигнала>. Неверный тип инженерного значения»
при использовании в проекте обработчиков событий.
6.3.25
Исправленные ошибки
Подсистема резервирования
После переподключения сетевых адаптеров оба сервера резервной пары находились В работе.
Модуль истории
Сообщение «История событий. Не удалось найти источник события {0}» ошибочно
записывалось в журнал модуля с уровнем «Предупреждения и аварийный сообщения». Теперь
данное сообщение записывается только в журнал с уровнем «Отладочные сообщения».
34
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 287 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Modbus TCP Master
Иногда после перезагрузки ПЛК и получения ошибки 6 (Slave Device Busy) модуль не
возобновлял обмен данными с этим ПЛК.
6.3.26
Исправленные ошибки
OPC AE Server
При квитировании подавленного события информация по квитированию не отображалась в
Alpha.HMI.Alarms.
При получении событий с помощью функции Refresh в оперативных событиях ошибочно
отображались события, сгенерированные по источнику в период подавления.
При подавлении событий по источнику агрегатор не учитывал активацию/деактивацию событий.
6.3.27
Улучшение
MQTT Client
Реализован новый алгоритм работы очередей приёма и отправки данных.
6.3.28
Улучшение
Modbus TCP Master
Реализована возможность настройки паузы между запросами.
Исправленная ошибка
Модуль вычислений
Исправлена ошибка, из-за которой вычисление по формуле могло выполняться по-разному в ОС
AstraLinux и в ОС Windows.
6.3.29
Улучшение
Siemens S7 Client
Теперь строки любой длины записываются в сигнал с актуальной длиной без усечения на 1
символ.
Исправленные ошибки
TCP Server
Узел, который является зоной, ошибочно отображался в Alpha.HMI.Alarms не только как зона,
но и как источник.
Siemens S7 Client
В редких случаях модуль переставал получать входящие значения после перезагрузки ПЛК, а в
журнале работы модуля формировалось сообщение об ошибке.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
35

=== Page 288 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
SQL Connector
SQL-запросы не выполнялись после потери и последующего восстановления связи с БД.
Модуль истории
При отсутствии папки для файла очереди и значении параметра Очередь данных:
«Оперативная» – модуль не подключался к БД PostgreSQL;
«Файловая» – модуль не создавал папку для очереди и не информировал об ее отсутствии в
журнале работы модуля и в журнале приложений.
EtherNet/IP Scanner
Исправлена ошибка, из-за которой Alpha.Server мог загружать все ядра процессора на 100%.
6.3.30
Исправленные ошибки
OPC AE Server
Исправлены ошибки, из-за которых при использовании механизма подавления и блокировок в
оперативном журнале клиентского приложения мог неверно отображаться состав событий после
переподключения.
BACnet Client
Модуль отправлял широковещательные запросы обнаружения устройств на порт 47808, даже
если в конфигурации устройств был указан другой порт, что приводило к невозможности опроса
устройств.
6.3.31
Исправленные ошибки
Alpha.Server
Устранены причины, из-за которых компонент прекращал работу, если при обмене данными
между двумя Alpha.Server по протоколу Alpha.Link у модуля HUB одного из них был настроен
удаленный доступ к истории другого.
Изменен внутренний механизм резервного копирования конфигурации Alpha.Server для ОС
Linux, т.к. при прежнем способе в редких случаях резервная копия конфигурации не создавалась,
если папка для резервных копий и исполняемый файл Alpha.Server находились в разных разделах
файловой системы.
Alpha.AccessPoint
Устранена причина, из-за которой после перезапуска службы Alpha.Historian:
сигналы для диагностики БД, которые получал Alpha.Server через модуль HUB и которые
участвовали в вычислениях, становились плохого качества COMM_FAILURE (24);
в журнале работы модуля HUB формировались сообщения о том, что качество сигналов
отличается от GOOD (192).
Проблема проявлялась на транзакционной модели исполнения Alpha.Server.
Подсистема резервирования
Устранены причины, из-за которых иногда при частых резервных переходах и включенном
модуле Modbus RTU Master резервный сервер мог прекратить работу.
Modbus TCP Master
Исправлена ошибка, из-за которой при получении ответа на запрос после истечения Времени
ожидания ответа от станции или на запрос, который не отправлялся, модуль разрывал связь по
каналу, при этом не было достигнуто Максимальное количество неуспешных запросов.
36
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 289 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
6.3.32
Изменение
OPC UA Client
Количество OPC UA серверов, к которым может единовременно подключиться OPC UA Client
одного экземпляра Alpha.Server, увеличено со 100 до 200.
6.3.33
Исправленные ошибки
OPC AE Server
Исправлена работа агрегатора событий - параметры агрегации количество активных событий и
максимальная важность среди активных событий неверно подсчитывались при:
квитировании активного события;
квитировании неактивного события, которое было сгенерировано до подавления источника.
Устранена причина, из-за которой модуль отправлял клиентам оперативные уведомления о
событиях от подавленных источников, при этом обработка подавленных событий выполнялась на
стороне сервера.
Подсистема резервирования
Исправлена ошибка, из-за которой иногда после старта резервной пары сигналы могли не
реплицироваться на резервный сервер.
6.3.34
Улучшение
Modbus RTU Master
Изменено поведение модуля при получении ошибочных ответов от станций:
При получении ответа от станции, к которой не было обращения в рамках текущего запроса,
чтение ответа не перезапускается и попытка запроса принимается за неудачную.
В конфигурацию модуля добавлен параметр, который определяет максимально допустимое
количество ответов, полученных от одной станции, к которой не было обращений. При
превышении заданного количества станция автоматически отключается на заданное время.
В конфигурацию модуля добавлен параметр, который определяет максимально допустимое
количество ошибочных ответов по общему каналу, полученных подряд. При превышении
заданного количества модуль разрывает связь с этим каналом, что приводит к разрыву связи со
всеми станциями этого канала.
Добавлены:
Служебный сигнал, который позволяет на уровне станции включать или отключать
возможность этой станции принимать запросы.
Группа служебных сигналов, которые отражают статистику обмена данными по каналу.
Параметр статистики, отражающий количество ошибочных ответов.
Исправленные ошибки
Siemens S7 Client
Исправлено поведение модуля при редких неуспешных запросах статуса ПЛК, благодаря чему
единичные ошибки возвращения статуса больше не приводят к переподключению к ПЛК и разрыву
соединения.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
37

=== Page 290 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Модуль рассылки событий
Устранена причина, из-за которой при использовании подключения с помощью STARTTLS
отправка сообщений о событиях выполнялась с ошибками или возникала ошибка подключения.
Исправлена ошибка, из-за которой в рассылаемых сообщениях неверно указывалось время
генерации событий.
Изменения документации
Редакция 1
Модуль TCP Server. Руководство администратора
Обновлена структура и содержимое документации:
Добавлено описание настройки модуля в Alpha.DevStudio (стр. 5).
Добавлено описание настройки файлового интерфейса в Alpha.DevStudio (стр. 14).
Добавлено описание настройки разворота инициации соединения между модулями TCP
Server и HUB в Alpha.DevStudio и Конфигураторе (стр. 22, 42).
Обновлена глава "Диагностика работы" (стр. 32).
Описание настройки в Конфигураторе перенесено в приложение (стр. 36).
Модуль IEC-104 Slave. Руководство администратора
В главе "Качество сигналов" актуализированы списки идентификаторов (стр. 5, 6).
Обновлено название модуля.
В Web-версии документация модулей в оглавлении теперь расположена в том же порядке, что и
модули на панели элементов в Alpha.DevStudio.
Редакция 2
Модуль SQL Connector. Руководство администратора
Обновлена структура и содержимое документации:
Обновлен раздел "Назначение и принцип работы" (стр. 5).
Добавлены используемые модулем запросы языка SQL (стр. 6).
Добавлено описание и примеры запросов с параметрами (стр. 8).
Добавлено описание типов привязок QRead и QParam (стр. 9).
Добавлено описание настройки модуля в Alpha.DevStudio с примерами запросов (стр. 11).
Обновлена глава "Диагностика работы" (стр. 39).
Добавлено описание и примеры строк подключения (стр. 42).
Обновлено приложение "Настройка доступа к данным по ODBC" (стр. 49).
38
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 291 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Alpha.Server. Руководство администратора
В главу "Системные требования" добавлено пояснение для приведенных системных требований
компьютера для установки серверной части Alpha.Server (стр. 13).
В главу "Установка дополнительной копии Alpha.Server" добавлены шаги с изменением Instance
ID:
в ОС Windows в пункт 4 (стр. 16);
в ОС Linux в пункт 2 (стр. 17).
В главу "Ручная настройка Alpha.Server" в таблицу добавлено описание атрибутов Instance ID,
Dispatch Model и Config ReadOnly (стр. 21).
В приложении "Свойства сигналов Alpha.Server" обновлено описание свойства 6 (ScanRate) (стр.
60).
Модуль IEC-104 Slave. Руководство администратора (стр. 38, 39)
В документации модулей МЭК-101/104 в приложении "МЭК частный диапазон типов" для
протокольных типов TC, TC_Status, TC_Time, TC_Time_Status удалено значение «False».
Модуль IEC-104 Master. Руководство администратора (стр. 22), Модуль Modbus TCP Master.
Руководство администратора (стр. 23)
Из пункта "Свойства сигналов" для модулей IEC-104 Master и Modbus TCP Master удалено
упоминание об обязательности свойства 6 (ScanRate).
Подсистема резервирования. Руководство администратора
В главе "Настройка модуля" в пункте 2 обновлена картинка и добавлено пояснение по выбору IP-
адресов основного и резервного каналов (стр. 7).
В главе "Сервисное приложение Управляющий" добавлено примечание о работе приложения
только в ОС Windows (стр. 11).
FINS Client. Руководство администратора
На титульный лист документации в формате *.pdf добавлено название модуля.
В Web-версии документация модулей в оглавлении теперь расположена в том же порядке, что и
модули на панели элементов в Alpha.DevStudio.
6.2
Новая возможность
В Alpha.Server реализованы массивы.
Для создания массива добавьте сигналу свойства:
PROPERTY_ISARRAY(5003) со значением «True»;
PROPERTY_INITSIZE(5004) - начальный размер массива;
PROPERTY_CAPACITY(5005) - максимальный размер массива.
Для сигналов-массивов в Alpha.Server поддержаны:
перекладка значений массива целиком;
применение битовой маски к каждому элементу массива;
линейный пересчет для каждого элемента массива;
линейный пересчет с изломом для каждого элемента массива.
Поддержка массивов модулями Alpha.Server
OPC UA Server
Узлы-массивы отображаются в адресном пространстве. Для узлов-массивов
поддержаны:
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
39

=== Page 292 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
свойства ValueRank и ArrayDimensions;
чтение, запись и публикация с использованием IndexRange.
OPC UA Client
Возможность подписки на узлы-массивы сторонних UA серверов, чтения их значений
целиком и записи полученных значений в узлы-массивы Alpha.Server.
Возможность подписки на узлы типа BYTESTRING и записи их значений в узлы-массивы
типа Uint1[] в Alpha.Server.
Возможность записи значений узлов-массивов из адресного пространства Alpha.Server
в сторонние UA серверы, включая запись значений узлов-массивов типа Uint1[] в узлы типа
BYTESTRING.
OPC DA Server, HDA Server
Сигнал-массив кодируется в HEX-строку и предоставляется клиентам в виде сигнала
типа String.
Модуль логики
Обращение по индексу к сигналам массивам в формулах и процедурах:
Чтение по индексу:
Item = Array[i];
Запись по индексу:
Array[i] = Item;
Использование значений-массивов целиком:
Array1 = Array2;
Модуль истории
Возможность сохранения значений сигналов-массивов в Alpha.Historian.
SnapShot
Сохранение и восстановление значений сигналов-массивов из файлов-срезов. Значения
массива сохраняются поэлементно через разделитель «;».
Улучшения
Alpha.Server
Качество буферируемых сигналов теперь восстанавливается при восстановлении связи.
SnapShot
Для индексов реализованы:
проверка на уникальность/неуникальность индекса;
возможность индексировать по неуникальным значениям;
запись в файл-срез сигналов по неуникальным индексам;
исключение из файла-среза сигналов по неуникальным индексам;
возможность указывать значение индекса, равное пустой строке.
Теперь если в шаблоне файла-среза указано имя индекса, которое не указано в списке индексов
конфигурации модуля, то в журнал приложений выводится предупреждение.
В Конфигураторе в названии индекса модуля SnapShot теперь нельзя использовать точки и
имя «Tag».
40
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 293 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
При указании в шаблоне файла-среза в блоке Exceptions определенного индекса, сигналы с
этим индексом не сохраняются в файл-срез.
Modbus TCP Master
Реализована возможность работы с несколькими станциями с одинаковым номером по разным
каналам.
Реализован обмен данными со шлюзом RTU-TCP, который является станцией Modbus TCP с
фиксированным номером «255».
Добавлена возможность настройки параметров связи отдельно для каждой станции:
Время ожидания ответа от станции, мс;
Максимальное количество одновременных запросов;
Максимальное количество неуспешных запросов;
Количество повторов на отправку команды;
Таймаут потери связи, мс;
Режим работы резервных каналов.
ОБРАТИТЕ ВНИМАНИЕ
Изменилась структура конфигурации модуля и состав параметров адреса сигнала.
Дистрибутив Alpha.Server
В дистрибутив Alpha.Server добавлены SQL скрипты для создания БД в MS SQL,
предназначенные для сохранения истории значений:
history.value.sqlserver2008.sql;
history.value_archive.sqlserver2008.sql.
Расположение скриптов:
ОС Windows: C:\Program Files\Automiq\Alpha.Server\Server\SQLScripts;
ОС Linux: /opt/Automiq/Alpha.Server/SQLScripts.
В дистрибутив Alpha.Server для ОС Linux добавлен пример динамической библиотеки на C# для
использования модулем логики.
Расположение библиотеки:
/opt/Automiq/Alpha.Server/ExternalLibsExamples/CSharp/Nethost.
Модуль истории
Реализовано уменьшение размера файла очереди queue.dat после уменьшения очереди на
запись в модуле истории.
Модуль рассылки сообщений SMTP
Служба Alpha.Server зависала при остановке после отправки сообщения, если в конфигурации
модуля были указаны тип подключения «STARTTLS» и порт «465».
При некорректно заданном порте почтового сервера:
Alpha.Server прекращал работу после отправки события AE;
возникала ошибка после отправки сообщения через строковый сигнал.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
41

=== Page 294 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
IEC-104 Master
Реализована возможность общего и группового опроса по командам с помощью служебных
сигналов.
Добавлены новые значения сигнала доставки:
«3» - получено положительное подтверждение активации.
«4» - получено положительное завершение активации с причиной передачи «10».
«-30» - получено отрицательное подтверждение активации с причиной передачи «7».
«-40» - получено отрицательное подтверждение активации с причиной передачи «10».
OPC AE Server
Реализована возможность проводить агрегацию событий по актуальным событиям из ОАТ.
Конфигуратор
Реализован экспорт ветки сигналов в формате *.CSV.
Исправленные ошибки
Alpha.Server
В транзакционной модели исполнения в некоторых случаях не выполнялись:
инвертирование логического значения при пересчёте;
пересчёт из инженерного значения в физическое.
SnapShot
Служебные сигналы управления формированием и восстановлением файлов-срезов из
стороннего формата ошибочно создавались в папке Service.Modules.<Имя модуля>, вместо папки
Service.Modules.<Имя модуля>.Control.
Modbus TCP Master
При отправке двумя объектами одной и той же команды в ПЛК, статус доставки команды
получал только один из объектов.
IEC-61850 Client
В ОС Linux модуль не восстанавливал соединение после разрыва связи.
6.2.1
В Alpha.Server 6.2.1 добавлена функциональность Alpha.Server версий 6.0.28 и 6.1.5 - 6.1.7.
Улучшения
Modbus TCP Master
Реализована возможность определять выделенный канал для станции, если в конфигурации
модуля определены несколько каналов с одинаковым IP-адресом и портом.
Исправленные ошибки
Alpha.Server
Alpha.Server мог завершать работу при перекладке бит.
Устранена запись в журнал приложений неинформативных сообщений о работе Alpha.Server.
Modbus RTU Master
В ОС Linux Alpha.Server завершал работу после резервного перехода при подписке UA клиентом
на некорректно настроенный сигнал доставки модуля Modbus RTU Master.
42
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 295 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
OPC AE Server
В OAT не сохранялись пользовательские атрибуты и информация о внешнем событии.
Агрегаторы работали некорректно, если было настроено больше одного фильтра по важности
событий.
Alpha.AccessPoint
Устранены проблемы передачи данных по файловому интерфейсу:
В ОС Linux могли передаваться не все данные.
В ОС Windows при успешной передаче данных в журнал работы модуля HUB записывались
сообщения об ошибках.
При запуске Alpha.AccessPoint от непривилегированного пользователя не передавались
данные.
IEC-104 Master
Ошибочно игнорировались значения, полученные опросом группы.
6.2.2
Исправленные ошибки
Alpha.Server
Alpha.Server завершал работу при запуске, если в конфигурации присутствовал цикл в
перекладке значений между сигналами.
NetDiag
В ОС Linux Alpha.Server прекращал работу при отключении сетевых кабелей от компьютера.
OPC UA Client
Модуль мог не подключиться к некоторым UA серверам по логину и паролю.
OPC AE Server
Агрегатор «AllAck» мог ошибочно иметь значение «True» при наличии неквитированных событий.
6.2.3
Улучшение
Alpha.Server
Оптимизирована обработка результатов вычислений.
Исправленная ошибка
Модуль логики
Результат вычислений мог не записываться в сигналы при использовании перекладки в
транзакционной модели исполнения.
6.2.4
Исправленные ошибки
HUB
Параметр Максимальное количество сигналов в пакете не учитывался при подписке на
статические сигналы.
TCP Server
В некоторых случаях модуль прекращал отправку значений клиентам по статическим сигналам.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
43

=== Page 296 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
6.2.5
Исправленные ошибки
Alpha.AccessPoint
В редких случаях Alpha.AccessPoint мог завершать работу при запуске.
Модуль истории
Модуль не предоставлял историю модулю HUB с прямым доступом к истории в составе этого же
Alpha.Server.
Добавлены доработки Alpha.Server версий 6.1.9 и 6.1.10:
Alpha.Server 6.1.9
Улучшение Alpha.Server
Оптимизирована обработка результатов вычислений.
Исправленные ошибки OPC AE Server
Устранён рост потребления памяти при использовании поврежденной OAT.
Не деактивировались события по сигналам, полученным по протоколу UNET.
Исправленная ошибка TCP Server
В некоторых случаях модуль прекращал отправку значений клиентам по статическим сигналам.
Alpha.Server 6.1.10:
Исправленная ошибка модуля HUB
Модуль ошибочно отправлял команды при нахождении Alpha.Server в состоянии "Резерв".
6.2.6
Улучшение
Модуль логики
Уменьшено потребление оперативной памяти модулем логики.
6.2.7
ОБРАТИТЕ ВНИМАНИЕ
Пользователям Alpha.Server версии 6.2.0 и выше, использующим в конфигурации модуль OPC UA
Client, рекомендуем безотлагательно произвести обновление до версии 6.2.7 для исключения
возможной отправки модулем OPC UA Client, находящимся в резерве, команд в UA Server.
Подробности возможного возникновения проблемы на Alpha.Server версии 6.2.0 и выше смотрите в
разделе "Исправленные ошибки" модуля OPC UA Client настоящей новости.
Исправленные ошибки
OPC UA Client
Находясь в резерве, модуль отправлял в UA Server уже отправленные ранее команды, получив
их по каналу репликации от основного Alpha.Server после перезапуска Alpha.Server, в составе
которого он функционирует:
В транзакционной модели исполнения модуль отправлял такие команды только для
нереплицируемых сигналов.
44
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 297 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
В модели исполнения по умолчанию модуль отправлял такие команды как для
реплицируемых сигналов, так и для нереплицируемых.
Дополнительным условием отправки таких команд являлось значение «Запрашивать данные»,
установленное для режима работы модуля в резерве.
В режиме работы в резерве «Закрывать соединение» после двойного резервного перехода
модуль переставал обмениваться данными с UA Server.
Изменения документации
Редакция 1
Модуль UNET Client. Руководство администратора
Обновлены главы раздела "Назначение и принцип работы" (стр. 4).
Добавлен пункт "Планировщик запросов" (стр. 4).
Обновлены описания параметров Интервал опроса и Частота изменения данных на устройстве
(стр. 22, 33).
Добавлена информация о поддержке чтения строковых данных.
Актуализировано описание настройки карты адресов.
Обновлён раздел "Служебные сигналы" (стр. 46).
Редакция 2
Добавлена документация для модуля FINS Client (FINS Client. Руководство администратора).
В документации модуля OPC UA Server в главе "Работа с клиентскими сертификатами" добавлена
информация о требуемом субъекте сертификата (Модуль OPC UA Server. Руководство администратора,
стр. 23).
6.1
Новые возможности
Реализован новый модуль Syslog Client, который обеспечивает:
генерацию сообщений Syslog на основе изменения строкового сигнала Alpha.Server;
накопление сформированных сообщений Syslog для отправки;
отправку сообщений Syslog получателям.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
45

=== Page 298 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
BACnet Client
ОБРАТИТЕ ВНИМАНИЕ
Модуль полностью обновлён. Конфигурации модуля предыдущих версий Alpha.Server не
поддерживаются ввиду большого числа изменений.
Возможности работы с устройствами:
Настройка каналов связи с устройством.
Повторная отправка запроса, если результат не получен за отведённое время.
Идентификация и отображение связи с устройством или объектом.
Поддержаны все типы связывания с устройством:
Статическое;
Динамическое;
Динамическое через BBMD-устройство.
Возможности получения данных:
Определение сигналов для выполнения запроса данных или опроса по команде
пользователя.
Поддержаны все механизмы получения данных с устройства:
Запрос;
Опрос;
Подписка на изменение значений (с подтверждением и без подтверждения).
Типы получаемых данных:
Поддержаны все типы объектов и свойств для получения данных.
Поддержаны все типы данных, в том числе структурные.
Добавлена возможность работы со структурными типами данных или с массивами как с
одним сигналом с помощью json-представления.
Возможности записи данных в устройство:
Запись значения свойства любого объекта:
С указанием приоритета;
Без указания приоритета.
Контроль статуса доставки команды записи значения.
Возможности событий BACnet:
Получение событий с устройств BACnet с последующим преобразованием:
в события Альфа платформы для отображения в Alpha.HMI.Alarms;
в сигналы Alpha.Server.
Квитирование событий на устройстве BACnet из:
Alpha.HMI.Alarms;
сигналов Alpha.Server.
Задание таблицы соответствия приоритетов событий BACnet и Альфа платформы.
Агрегация событий BACnet.
В сети BACnet:
Реализовано отображение модуля в сети BACnet в соответствии с параметрами, заданными
в конфигурации.
Улучшения
46
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 299 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Модуль рассылки событий
Модуль теперь называется "Модуль рассылки сообщений SMTP" и позволяет рассылать
сообщения по событиям изменения значений строковых сигналов.
IEC-104 Master
При отсутствии на диске директории, указанной в параметре Полное имя папки для записи
файлов, модуль теперь создаёт указанную директорию.
UNET Client
Поддержано чтение строковых переменных для режима чтения оперативных данных.
Исправленные ошибки
IEC-104 Master
Alpha.Server завершал работу, если модулю IEC-104 Master было включено получение файлов
и отсутствовали подкаталоги для чтения.
Конфигуратор
На вкладке Модули при блокировании ветки конфигурации дерево модулей сворачивалось до
выделенного узла. Теперь при блокировании ветки конфигурации дерево модулей остаётся в
развёрнутом виде.
На вкладке Сигналы при подключении к Alpha.Server дерево сигналов сворачивалось до
корневого узла. Теперь при подключении дерево сигналов разворачивается до узла, выделенного до
отключения от Alpha.Server.
Модуль логики
В ОС AstraLinux не выполнялась процедура обработчика из свойства 777013.
Внутренние изменения
Alpha.Server
Alpha.Server переведён на внутренний протокол взаимодействия Alpha.RTLP.
OPC UA Client
Сокращено число потоков обслуживающих сессию.
TCP Server
Поддержан новый набор команд для получения информации о дереве сигналов.
6.1.1
ОБРАТИТЕ ВНИМАНИЕ
В Alpha.Server 6.1.1 добавлена функциональность Alpha.Server версий 6.0.11 - 6.0.22.
Известные проблемы
ОБРАТИТЕ ВНИМАНИЕ
Известные проблемы будут исправлены в ближайших патчах Alpha.Server версии 6.1.х.
ВАЖНО
Не следует устанавливать Alpha.Server версии 6.1.1, если используете:
модуль Modbus RTU Master;
модуль SnapShot и символы кириллицы в названии шаблона файла-среза или имени
сгенерированного файла-среза.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
47

=== Page 300 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Modbus RTU Master
Стабильные проблемы с отправкой управляющих воздействий: команды не отправляются на
заданные станции.
SnapShot
При генерации файла-среза некорректно обрабатываются символы кириллицы:
возникает ошибка при использовании символов кириллицы в названии шаблона файла-
среза в служебном сигнале «TemplateName»;
сбой кодировки в имени сгенерированного файла-среза при использовании символов
кириллицы в служебном сигнале «OutFileName».
Конфигуратор
В модуле Modbus RTU Master в параметре Стратегия формирования запросов на чтение
установленное значение «На сплошные данные» изменяется на значение «По максимуму» при
загрузке конфигурации, созданной в Alpha.Server версии ниже 6.0.13, что приводит к ошибкам в
работе модуля.
Улучшения
Важная доработка тракта TCP Server <-> HUB
Реализована возможность разворота инициации соединения между модулями HUB и TCP
Server. Теперь TCP Server может самостоятельно инициировать подключение к модулю HUB.
Раньше инициатором соединения мог выступать только модуль HUB, поэтому, если TCP Server
находился в подсети, к которой запрещено подключение извне, то было невозможно установить
соединение.
Например, эта функциональность позволит использовать сегмент ДМЗ в неактивном режиме, когда
старт передачи данных в ДМЗ инициирует связанный с ним промышленный контур, а не сам сервер
ДМЗ.
SnapShot
Реализована возможность выбора шаблона и сохранения файла-среза перед остановкой
Alpha.Server или модуля SnapShot.
6.1.2
Исправлены известные проблемы Alpha.Server6.1.1
Modbus RTU Master
Устранены проблемы с отправкой управляющих воздействий: теперь команды отправляются на
заданные станции.
SnapShot
При генерации файла-среза символы кириллицы стали обрабатываться корректно:
больше не возникает ошибка при использовании символов кириллицы в названии шаблона
файла-среза в служебном сигнале «TemplateName;»
не происходит сбой кодировки в имени сгенерированного файла-среза при использовании
символов кириллицы в служебном сигнале «OutFileName».
Конфигуратор
В модуле Modbus RTU Master в параметре Стратегия формирования запросов на чтение
установленное значение «На сплошные данные» больше не изменяется на значение «По максимуму»
при загрузке конфигурации, созданной в Alpha.Server версии ниже 6.0.13, что больше не приводит к
ошибкам в работе модуля.
Исправленная ошибка
48
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 301 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
OPC AE Server
Устранена утечка памяти при работе модуля OPC AE Server.
6.1.3
В Alpha.Server 6.1.3 добавлена функциональность Alpha.Server версий 6.0.24 и 6.0.25.
Исправленные ошибки
Alpha.Server
В транзакционной модели исполнения не выполнялась проверка соответствия типов сигнала
Alpha.Server и записываемого в сигнал значения, получаемого по каналу репликации и при
восстановлении значения из буфера, что могло приводить к ошибкам в работе Alpha.Server.
OPC AE Server
После перезапуска Alpha.Server и отсутствия сгенерированных событий служебный сигнал
«Acknowledged» ошибочно принимал значение «False», соответствующее неквитированному
событию. Из-за чего на мнемосхемах в Alpha.HMI могло ошибочно отображаться наличие
неквитированных событий для объектов.
6.1.4
Исправленные ошибки
Modbus RTU Master
В ОС Linux в редких случаях Alpha.Server прекращал работу во время запуска.
После применения конфигурации для резервной пары модуль Modbus RTU Master активного
сервера оставался в режиме РЕЗЕРВ и не подключался к станции.
Alpha.AccessPoint
Alpha.AccessPoint получал значения служебных сигналов только с одного сервера резервной
пары.
6.1.5
В Alpha.Server 6.1.5 добавлена функциональность Alpha.Server версий 6.0.26 и 6.0.27.
Исправленные ошибки
OPC AE Server
Агрегаторы работали некорректно, если было настроено больше одного фильтра по важности
событий.
OPC UA Client
Модуль не передавал данные аутентификации при подключении к UA серверу KSE Platform в
режиме авторизации Логин/Пароль, из-за чего не выполнялась запись значений в UA сервер.
EtherNet/IP Scanner
Качество сигналов ошибочно оставалось хорошим после отключения модуля через служебный
сигнал «Active.Set».
6.1.6
В Alpha.Server 6.1.6 добавлена функциональность Alpha.Server 6.0.28.
Исправленная ошибка
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
49

=== Page 302 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
EtherNet/IP Scanner
Alpha.Server завершал работу после остановки модуля через служебный сигнал «Active.Set» и
последующей попытки отправки команды.
6.1.7
Исправленная ошибка
Alpha.Server
В редких случаях при запуске в транзакционной модели исполнения Alpha.Server мог завершать
работу при обработке некоторых вычислений.
6.1.8
Исправленные ошибки
NetDiag
В ОС Linux Alpha.Server прекращал работу при отключении сетевых кабелей от компьютера.
OPC UA Client
Модуль не подключался к ПЛК при использовании режима безопасности «None» и режима
авторизации «Анонимный».
6.1.9
В Alpha.Server 6.1.9 добавлена функциональность Alpha.Server версий 6.0.30 и 6.0.31.
Alpha.Server 6.0.30:
Улучшение
Alpha.Server
Оптимизирована обработка результатов вычислений.
Исправленная ошибка
OPC AE Server
Устранён рост потребления памяти при использовании поврежденной OAT.
Alpha.Server 6.0.31:
Исправленные ошибки
OPC AE Server
Не деактивировались события по сигналам, полученным по протоколу UNET.
TCP Server
В некоторых случаях модуль прекращал отправку значений клиентам по статическим
сигналам.
6.1.10
Исправленная ошибка
HUB
Модуль ошибочно отправлял команды при нахождении Alpha.Server в состоянии "Резерв".
50
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 303 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
6.1.11
Исправленная ошибка
SQL Connector
SQL-запросы не выполнялись после потери и последующего восстановления связи с БД.
6.1.12
Исправленная ошибка
OPC UA Client
Устранена причина, из-за которой модуль долго (5-10 секунд) переключался на резервный ПЛК
при остановке основного ПЛК.
Изменения документации
Редакция 1
Обновлена архитектурная схема Alpha.Server (Alpha.Server. Руководство администратора, стр. 12).
В главе "Системные требования" обновлен список поддерживаемых ОС в документации
Alpha.Server и Alpha.AccessPoint (Alpha.Server. Руководство администратора, стр. 13),
(Alpha.AccessPoint. Руководство администратора, стр. 9).
В документации модуля OPC UA Server для параметра Порт OPC TCP протокола указано значение
порта по умолчанию (Модуль OPC UA Server. Руководство администратора, стр. 8).
Исправлены опечатки.
Редакция 2
В документацию Alpha.Server добавлена глава "Контроль целостности конфигурации и БД"
(Alpha.Server. Руководство администратора, стр. 33).
Исправлены ошибки:
неверные ссылки в документации и модулей Modbus RTU Master, OPC UA Client, DTS Client;
добавлен отсутствующий рисунок в главе "Относительная адресация при копировании"
документации Alpha.Server.
Редакция 3
В главе "Системные требования" обновлен список поддерживаемых ОС в документации
Alpha.Server и Alpha.AccessPoint (Alpha.Server. Руководство администратора, стр. 13),
(Alpha.AccessPoint. Руководство администратора, стр. 9).
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
51

=== Page 304 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Модуль Modbus RTU Master. Руководство администратора
Обновлена структура и содержимое документации:
Добавлено описание настройки модуля в Alpha.DevStudio (стр. 22).
Добавлено описание настройки работы модуля через шлюз TCP (стр. 34).
Обновлён раздел "Назначение и принципы работы" (стр. 4).
Удалены разделы "Функциональные возможности" (информация перенесена в "Назначение
и принципы работы"), "Конфигурирование модуля", "Конфигурирование сигналов", "Пример
работы с модулем".
Модуль ProcessMonitor. Руководство администратора
Добавлено описание настройки модуля в Alpha.DevStudio (стр. 5).
Добавлено описание сигналов для отслеживания загрузки HDD и RAM (стр. 10).
Редакция 4
Актуализированы устаревшие картинки, исправлены опечатки.
Редакция 5
Модуль TCP Server. Руководство администратора
Обновлён раздел "Назначение" (стр. 4).
Из раздела "Настройка модуля" удалено примечание (стр. 5).
Модуль EtherNet IP Scanner. Руководство администратора (стр. 47)
В приложении В обновлена таблица значений сигнала доставки.
Alpha.AccessPoint. Руководство администратора
Из главы "Alpha.AccessPoint в TCP/IP сетях" удалено примечание (стр. 7).
Модуль SQL Connector. Руководство администратора (стр. 4), Модуль истории. Руководство
администратора (стр. 4)
Обновлены примечания о поддерживаемых версиях PostgreSQL.
Модуль рассылки событий. Руководство администратора (стр. 4), Модуль ТЕМ-104. Руководство
администратора (стр. 4)
В Web-версии документации в главах "Назначение и принцип работы" исправлены размеры
рисунков.
6.0
Новые возможности
Реализованы новые модули:
UNET Client, с помощью которого Alpha.Server может обмениваться данными с ПЛК TREI-5B по
протоколу UNET.
NFL Client, с помощью которого Alpha.Server может обмениваться данными с САУ по протоколу
NFL (протокол обмена данными разработки ПАО "Газпром автоматизация").
Security Client, предназначенный для получения значений необходимых настроек из
Alpha.Security и записи полученных значений в сигналы Alpha.Server.
Транзакционная модель исполнения
Реализована новая модель обработки событий и вычислений: транзакционная модель
исполнения.
Основные особенности новой модели:
52
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 305 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Все события (изменения значений сигналов, результаты вычислений, события AE) проходят
через единый высокопроизводительный тракт - журнал транзакций - в той последовательности, в
которой они возникают.
Обработка событий (транзакций) потребителями (ядром и модулями) выполняется
параллельно, в порядке их добавления в журнал транзакций.
Синхронизация состояния в резервной паре выполняется за счёт репликации журнала
транзакций с активного на резервный сервер.
Новая модель на основе журнала транзакций обеспечивает:
В рамках отдельного экземпляра Alpha.Server: строгую последовательность обработки
событий.
В рамках резервной пары Alpha.Server:
Полную синхронизацию состояния на резервном сервере.
Строгую последовательность синхронизации состояния.
Снижение нагрузки на резервном сервере: обработку выполняет активный сервер, а
резервный только применяет результаты обработки. Таким образом исключается
необходимость дублированной работы модуля вычислений и модуля OPC AE Server на
резервном сервере.
Транзакционная модель исполнения является основной, в новых проектах рекомендуется
использовать её. Работоспособность прежней модели сохранена для совместимости.
Механизм дисковой буферизации потока данных
На основе новой модели реализован механизм дисковой буферизации потока данных между
узлами-источниками и узлами-потребителями Alpha.Server:
На узлах-источниках:
Для сигналов может быть настроено сохранение в один или несколько файловых
буферов.
События по буферизируемым сигналам сохраняются в файловые буферы в
порядке обработки журнала транзакций.
Синхронизация состояния файловых буферов в резервной паре обеспечивается за
счёт репликации журнала транзакций.
Сохраняются позиции узлов-потребителей для возобновления передачи потока
данных после восстановления связи.
На узлах-потребителях:
Активный сервер получает буферизированный поток данных с узлов-источников с
учётом их резервирования.
Резервный сервер получает те же данные с активного сервера за счёт репликации
журнала транзакций.
Также механизм буферизации обеспечивает возможность восстановления последнего
состояния по буферизируемым сигналам при перезапуске Alpha.Server.
Хранение на диске основано на собственном движке, сторонние компоненты не требуются.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
53

=== Page 306 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Подсистема генерации событий
Реализован механизм OAT - таблица оперативных событий AE. Механизм обеспечивает
сохранность сгенерированных событий AE до тех, пока они остаются актуальными: активными и/или
неквитированными.
Таблица OAT хранится на диске, таким образом обеспечивается восстановление её состояния при
перезапуске Alpha.Server.
Синхронизация состояния OAT в резервной паре обеспечивается за счёт репликации журнала
транзакций.
Хранение на диске основано на собственном движке, сторонние компоненты не требуются.
Реализована возможность добавления событиям дополнительных пользовательских атрибутов.
Изменения атрибутов события:
В уведомление о событии добавлен атрибут OBJECT_NAME, содержащий имя объекта,
которому принадлежит источник события.
Атрибуты SUPPRESSED_ATTRIBUTE (bool) и SUPPRESSED_UNTIL_ATTRIBUTE (uint64_t) объединены
в один атрибут SUPPRESSED_ATTRIBUTE (variant) с возможными значениями:
«true» - подавление активно, бессрочно;
«false» - подавление отсутствует;
число типа uint64_t - подавление активно до соответствующей метки времени.
Реализована возможность автоматического квитирования последнего активного подусловия при
новой активации условия. При активации подусловия OPС AE Server автоматически сгенерирует
квитирование текущего состояния (если оно ещё не квитировано), а затем сгенерирует активацию.
Реализована возможность настройки деактивирующих подусловий. Добавлены атрибуты
подусловий:
PREV_ACTIVATION_TIME - время активации предыдущего активного подусловия;
DEACTIVATION_TIME - время деактивации подусловия.
В XML-описании условий (свойство 999004) в блоке подусловия добавлен атрибут DeactivationMode
с возможными значениями:
«0» - активирующее подусловие (по умолчанию).
«1» - деактивирующее подусловие.
Alpha.Server
Реализован механизм получения архивных данных ПЛК и сохранение полученных архивных
данных в историю без отображения на верхнем уровне. Используется модулями UNET Client и IEC-
104 Master.
Вызов функций API сервера теперь возможен по OPС UA и TCP.
Новый алгоритм резервирования:
Реализована новая характеристика сервера – «Приоритет», значение «True» которой
означает, что сервер является приоритетным и стремится в режим мастера.
Резервный переход происходит путем передачи приоритета от одной реплики к парной.
Alpha.Server может отслеживать состояние памяти и при нехватке переходить в состояние
аварии.
Модуль истории
Реализовано распределение истории значений по разным хранилищам с разными параметрами
фильтрации.
IEC-104 Master
Реализована возможность приёма файлов от устройств (например, файлов формата COMTRADE).
Реализовано получение архивных данных ПЛК по протоколу IEC-104 и сохранение полученных
архивных данных в историю без записи в сигналы.
54
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 307 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
TCP Server
Поддержана передача буферизированных данных.
Snapshot
Реализовано формирование файлов-срезов требуемого формата и восстановление файла-среза
из стороннего формата.
OPC AE Server
Поддержаны расширения OPC AE. При включенном расширении OPС AE:
Происходит деактивация активного подусловия при активации следующего подусловия.
Событие о деактивации имеет следующие поля и значения:
Поле
Значение
ChangeMask
OPC_CHANGE_ACTIVE_STATE + OPC_CHANGE_ATTRIBUTE
Message
предыдущее значение
Severity
предыдущее значение
Subcondition
предыдущее значение
Реализован параметр агрегации «AutoAck» для автоматического квитирования событий объекта.
При подаче команд подавления и блокирования теперь формируются уведомления для
клиентов.
Улучшения
Alpha.Server
Открытие и просмотр конфигурации Alpha.Server через сервисное приложение Конфигуратор
без возможности редактирования. Возможность редактирования конфигурации через
Alpha.DevStudio при этом сохраняется.
HUB
В адресе сигнала добавлено поле, определяющее направление передачи данных - входящий или
исходящий. Если направление не задано, то сигнал считается входящим.
OPC UA Server
В конфигурации Alpha.Server теперь может присутствовать несколько экземпляров модуля
OPC UA Server, что позволяет предоставлять разным OPC UA клиентам индивидуальные наборы
данных.
Модуль резервирования
Возможность изменения таймаута выполнения запросов о состоянии парного сервера.
Модель запуска Alpha.Server теперь указывается в журнале работы модуля.
В статистику модуля добавлены параметры, отображающие информацию о состоянии
резервирования.
Изменения
Сервер лицензирования больше не входит в состав дистрибутива Alpha.Server.
Исправленные ошибки
Модуль истории
В параметре статистики Количество событий, принятых к сохранению не учитывались события,
сохраняемые в PostgreSQL.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
55

=== Page 308 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Значения имели неверное Время сервера при чтении истории значений из PostgreSQL по OPС UA
из Alpha.AccessPoint.
Модуль логики
В ОС Linux при переводе времени назад переставал работать обработчик по таймеру.
6.0.1
Новые возможности
ProcessMonitor
Модуль позволяет получать информацию о процессах в OC Linux.
Реализована возможность отображения информации о загрузке жесткого диска и оперативной
памяти отслеживаемым процессом. Информация отображается в значениях служебных сигналов:
«pm_diskUsage» - среднее использование дисковых ресурсов за интервал времени
UpdateInterval в Мб/с;
«pm_ramUsage» - количество используемой оперативной памяти в Мб.
Модуль истории
Возможность отключения сохранения в Alpha.Historian дополнительной метки времени, которой
является метка времени сервера.
Исправленные ошибки
Alpha.Server
В редких случаях Alpha.Server прекращал работу:
при изменении значений некоторых сигналов;
при обработке некоторых вычислений.
Модуль истории
Модуль сохранял в историю события, сгенерированные на других узлах Alpha.Server. Теперь
модуль сохраняет в историю только события, сгенерированные по локальным сигналам.
Не удавалось получить историю, либо получение истории выполнялось долго, если
отсутствовала связь с некоторыми БД.
TCP Server
Устранена проблема, из-за которой Alpha.HMI, получающий данные от модуля TCP Server,
зависал при переключении между экранными формами.
Modbus TCP Master
Иногда после резервного перехода между ПЛК опрос ПЛК продолжался спустя длительное
время.
OPC AE Server
Агрегатор не применял фильтр к неактивным событиям и включал их в результат агрегации.
При переходе в состояние Enabled условие не помечалось квитированным.
Alpha.AccessPoint
В ОС Windows при регистрации второго экземпляра Alpha.AccessPoint запись в реестр
выполнялась некорректно.
6.0.2
Улучшения
Logics Module
56
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 309 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
При обнаружении цикла в вычислениях теперь в журнал будут выведены не только узлы,
образующие цикл, но и все узлы-триггеры текущей задачи исполнения. Первым в списке будет узел,
изменение которого привело к появлению задачи в очереди исполнения.
Alpha.Server, Alpha.Imitator, Alpha.AccessPoint
В ОС Linux в файле настроек *.xml больше не указываются COM-серверы.
Исправленные ошибки
Alpha.Server
В редких случаях Alpha.Server прекращал работу.
Alpha.Imitator
Alpha.Imitator зависал после запуска сессии перезаписи.
HUB
По динамической привязке модуль не получал значения сигналов, для которых одновременно
была настроена динамическая и статическая привязки.
Иногда после потери связи модуль переставал получать значения статических сигналов.
При нестабильной связи с удаленным сервером модуль HUB мог посчитать, что сервер не
поддерживает некоторые команды. Поэтому могли быть недоступны получение значений
статических сигналов, буферизация, получение истории.
NetDiag2
В ОС Linux модуль не запускался при работе Alpha.Server из-под непривилегированной учётной
записи.
Модуль истории
Устранена причина ошибки Не удалось передать данные на сторону БД Alpha.Historian:
Недостаточно памяти. Для баз Alpha.Historian размер кэша в файловых очередях теперь
выбирается динамически в зависимости от количества баз, а не строго равный 32 Мб.
6.0.3
Исправленная ошибка
OPC UA Client
Обмен данными мог прекращаться, если UA сервер возвращал ошибку при изменении режима
мониторинга узлов, чтении, публикации. Иногда обмен данными прекращался при изменении
времени на стороне UA сервера.
6.0.4
Исправленная ошибка
OPC UA Client
Модуль не устанавливал плохое качество входящим сигналам при потере связи с UA сервером.
6.0.5
Внутренние изменения. Функциональность компонента не изменилась.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
57

=== Page 310 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
6.0.6
Исправленные ошибки
OPC UA Client
Устранена проблема, из-за которой Alpha.Server иногда мог прекращать работу.
В редких случаях модуль не устанавливал плохое качество некоторым сигналам при потере
связи с UA сервером.
В редких случаях не восстанавливалась связь с UA сервером из-за зависания модуля.
Модуль истории
Периодическое повторное сохранение значения в историю выполнялось чаще, чем задано, если
значение периода сохранения было большим.
Alpha.AccessPoint
Иногда Alpha.AccessPoint не восстанавливал соединение с Alpha.Server по одному из каналов
связи.
6.0.7
Исправленная ошибка
IEC-61850 Client
Устранена проблема, из-за которой Alpha.Server иногда мог прекращать работу.
6.0.8
Исправленные ошибки
OPC UA Client
Модуль не подключался к некоторым UA серверам.
TCP Server
Клиенты, такие как Alpha.HMI.Trends, могли получать недостоверную информацию о дереве
сигналов Alpha.Server.
6.0.9
Новая возможность
Реализован модуль EtherNet/IP Scanner, с помощью которого Alpha.Server может обмениваться
данными с ПЛК по протоколу EtherNet/IP.
Исправленные ошибки
OPC UA Server, SNMP Manager
В ОС Linux в некоторых случаях Alpha.Server не выполнял обмен данными по OPC UA и SMNP
при большом количестве опрашиваемых станций Modbus TCP.
IEC-61850 Client
В редких случаях Alpha.Server прекращал работу при разрыве связи с устройством.
TCP Server
Некорректно обрабатывались изменения значения сигнала «Service.InvokeFromJSON», из-за
чего использование данного сигнала, например в Alpha.HMI, не приводило к ожидаемому
результату.
58
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 311 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
OPC AE Server
Деактивация событий по уровню происходила только для последнего активного события. Теперь
деактивируются все события.
При включении расширений OPC AE не выполнялась автоматическая деактивация условия при
активации следующего подусловия.
6.0.10
Исправленная ошибка
TCP Server
Устранена проблема, из-за которой в проектах Alpha.HMI иногда не удавалось получать
свойства сигналов, а также выполнять запись значений.
6.0.11
Внутренние изменения. Функциональность компонента не изменилась.
6.0.12
Новые возможности
Modbus TCP Master
Поддержаны новые возможности обмена данными с ПЛК «Эмикон»:
запрос до «719» регистров Input Registers;
обмен строковыми значениями длиной до «1438» символов;
обмен строковыми значениями в кодировке UTF-16.
Modbus TCP Slave
Поддержан обмен строковыми значениями в кодировке UTF-16.
Улучшение
Подсистема резервирования
Улучшен алгоритм инициализации репликации данных при выходе из нештатного состояния
серверов.
6.0.13
Улучшение
Modbus RTU Master
Реализована возможность опроса через коммутатор Ethernet/SerialLine устройств
последовательной линии.
Исправленная ошибка
OPC UA Server
В OC Linux при запуске модуля Alpha.Server прекращал работу при большом количестве
опрашиваемых станций Modbus TCP.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
59

=== Page 312 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
6.0.14
Исправленные ошибки
Alpha.Server
В ОС Linux в крайне редких случаях Alpha.Server мог прекращать работу после очистки старых
журналов работы модулей.
В редких случаях при одновременном соблюдении условий:
в модуле OPC AE Server было включено расширение OPC AE,
Alpha.Server был запущен в транзакционной модели исполнения,
произошла деактивация динамического условия,
использовалось резервирование серверов,
Alpha.Server мог прекращать работу в ходе синхронизации состояний (репликации) парных
серверов.
6.0.15
Исправленные ошибки
Подсистема резервирования
Устранена ошибка, из-за которой в момент резервного перехода со слэйва могла пройти
пересылка значений, накопленных во время работы в режиме аварийного мастера.
OPC AE Server
В событиях вместо заданного пользовательского атрибута ошибочно указывался атрибут,
используемый по умолчанию.
TCP Server
Устранена утечка памяти в случае разрыва связи с клиентом, подключающимся к порту доступа
к истории, в процессе инициализации соединения.
EtherNet/IP Scanner
Модуль мог несвоевременно запрашивать данные.
6.0.16
Улучшения
Modbus TCP Master
Реализована возможность работы с несколькими станциями с одинаковым номером по разным
каналам.
Реализован обмен данными со шлюзом RTU-TCP, который является станцией Modbus TCP с
фиксированным номером «255».
60
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 313 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Добавлена возможность настройки параметров связи отдельно для каждой станции:
Время ожидания ответа от станции, мс;
Максимальное количество одновременных запросов;
Максимальное количество неуспешных запросов;
Количество повторов на отправку команды;
Таймаут потери связи, мс;
Режим работы резервных каналов.
ОБРАТИТЕ ВНИМАНИЕ
Изменилась структура конфигурации модуля и состав параметров адреса сигнала.
Исправленная ошибка
EtherNet/IP Scanner
Иногда в ОС Astra Linux Alpha.Server мог долго останавливаться.
6.0.17
Улучшения
IEC-101 Master
Реализована возможность общего и группового опроса по командам с помощью служебных
сигналов.
Реализована возможность обмена данными по TCP/IP, при этом Alpha.Server выступает в роли
ПУ (в соответствии с ГОСТ Р МЭК 60870-5-101).
6.0.18
Исправленная ошибка
Модуль логики
Иногда Alpha.Server мог аварийно завершать работу.
6.0.19
Улучшения
Устранена проблема, которая могла приводить к нарушению целостности в файлах данных
Alpha.Server после некорректного завершения работы службы. Исправление затрагивает модули:
Модуль истории;
OPC AE Server при использовании OAT;
TCP Server при использовании файловой буферизации.
Рекомендуется обновление.
IEC-101 Master
Реализованы служебные сигналы, отображающие количество отправленных и принятых пакетов.
Исправленная ошибка
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
61

=== Page 314 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
IEC-101 Master
Модуль не учитывал, что при общем опросе значения типа <231> M_IT_TD_1 приходят в виде
значений типа <230> M_IT_ND_1, и игнорировал такие значения.
6.0.20
Улучшение
IEC-101 Master
Реализована возможность получения архивных данных ПЛК. Настройка получения архивных
данных ПЛК выполняется аналогично настройке в модуле IEC-104 Master.
Исправленная ошибка
Modbus TCP Master
В Конфигураторе было невозможно задать категорию данных в редакторе адреса.
6.0.21
Исправленная ошибка
OPC UA Client
Alpha.Server зависал при инициализации модуля, если сертификат модуля был
недействительным.
6.0.22
Исправленные ошибки
Alpha.Server
Alpha.Server аварийно завершал работу, если имя сигнала начиналось или заканчивалось
пробелом.
Alpha.AccessPoint
Иногда при успешном подключении к Alpha.Server канал подключения оставался неактивным.
6.0.23
ОБРАТИТЕ ВНИМАНИЕ
В Alpha.Server6.0.23 добавлены исправления известных проблем Alpha.Server 6.1.1.
Исправленные ошибки
Модуль истории
Не удавалось получить историю событий из БД PostgreSQL при большом количестве событий в
запрашиваемом интервале.
Дистрибутив
Для ОС Windows и Linux различался срок действия сертификатов, генерируемых при установке
Alpha.Server.
В ОС Linux в генерируемом при установке Alpha.Server сертификате OPC UA Client
отсутствовал ApplicationURI.
62
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 315 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
6.0.24
Исправленная ошибка
Alpha.AccessPoint
Alpha.AccessPoint зависал при инициализации модуля HUB.
6.0.25
Исправленные ошибки
Siemens S7 Client
Иногда Alpha.Server завершал работу при отправке исходящего значения.
Иногда значение входящего сигнала Alpha.Server не соответствовало значению сигнала в ПЛК.
SQL Connector
Не выполнялись динамически формируемые SQL-запросы вида SELECT * FROM table WHERE
table.time > ?, сравнивающие столбец типа datetime и параметр запроса типа string.
6.0.26
Улучшение
UNET Client
Добавлены служебные сигналы, позволяющие для каждого устройства отслеживать:
процент загрузки планировщика задач;
объем отправленных и полученных данных:
с указанием метки времени, от которой начат отсчёт;
возможностью сброса счётчика;
возможностью задавать минимальный период обновления счётчика.
Исправленная ошибка
Модуль истории
При пустом интервале запроса не удавалось получить граничные значения из БД PostgreSQL, из-
за чего в Alpha.HMI.Trends не строились графики.
6.0.27
Улучшение
Alpha.Server
Реализована возможность отключения автоматического создания резервной копии
конфигурации Alpha.Server.
Чтобы отключить автоматическое создание резервной копии конфигурации, в файле настроек
сервера *.xml в элементе <Backup> удалите атрибут Time.
Исправленная ошибка
IEC-101 Master
Параметр Количество повторов запроса данных ошибочно использовался при определении
состояния связи со станцией.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
63

=== Page 316 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
6.0.28
Исправленная ошибка
UNET Client
Alpha.Server завершал работу, если на диске было недостаточно места при сохранении в файл
времени последних успешно полученных данных.
6.0.29
Исправленные ошибки
NetDiag
В ОС Linux Alpha.Server прекращал работу при обрыве связи с ПЛК.
OPC UA Client
Модуль не подключался к ПЛК при использовании режима безопасности «None» и режима
авторизации «Анонимный».
6.0.30
Улучшение
Alpha.Server
Оптимизирована обработка результатов вычислений.
Исправленная ошибка
OPC AE Server
Устранён рост потребления памяти при использовании поврежденной OAT.
6.0.31
Исправленные ошибки
OPC AE Server
Не деактивировались события по сигналам, полученным по протоколу UNET.
TCP Server
В некоторых случаях модуль прекращал отправку значений клиентам по статическим сигналам.
Изменения документации
Редакция 1
Некоторые скриншоты файлов конфигураций заменены на блоки кода.
В веб-версии документации блокам кода добавлена подсветка синтаксиса.
Актуализированы устаревшие картинки, исправлены опечатки.
64
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 317 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Модуль SQL Connector. Руководство администратора (стр. 4), Модуль истории. Руководство
администратора (стр. 4)
Добавлены примечания о поддерживаемых версиях PostgreSQL.
Редакция 2
Актуализированы устаревшие картинки, исправлены опечатки.
Alpha.Server. Руководство администратора
Добавлена глава Об Alpha.Server (стр. 5).
Обновлено содержимое главы Alpha.Server в составе Альфа платформы (стр. 6).
Обновлено содержимое пункта Принципы модульного строения (стр. 24).
Обновлено содержимое главы Сигналы Alpha.Server (стр. 34).
Обновлено содержимое пункта Свойства сигналов (стр. 35).
Таблица с описанием свойств сигналов перенесена в приложение (стр. 60).
Alpha.AccessPoint. Руководство администратора
Обновлены схемы в главах Назначение и принцип работы (стр. 4), Передача данных через
файловый интерфейс (стр. 26), Получение исторических данных по OPC UA (стр. 34)
Модуль TCP Server. Руководство администратора
В главе Передача данных через файловый интерфейс обновлена схема (стр. 7)
Редакция 3
Добавлена документация для модуля UNET Client (UNET Client. Руководство администратора).
В главе "Системные требования" обновлен список поддерживаемых ОС в документации
Alpha.Server и Alpha.AccessPoint (Alpha.Server. Руководство администратора, стр. 13),
(Alpha.AccessPoint. Руководство администратора, стр. 9).
В документацию сервисного приложения Статистика добавлен пункт "Сохранение файла статистики
через интерфейс командной строки" (Сервисное приложение Статистика. Руководство администратора,
стр. 16).
В документации модуля истории в разделе "Дополнительные параметры сохранения истории" для
параметров MinTime и RepeatTimeout добавлены допустимые диапазоны значений (Модуль истории.
Руководство администратора, стр. 15).
В документации модулей МЭК-101/104 в приложении "МЭК стандартный диапазон типов" для типа
49:C_SE_NB_1 добавлен тип сервера uint2, а тип float заменен на int2 (Модуль IEC-104 Master.
Руководство администратора, стр. 32).
Исправлены опечатки.
Редакция 4
Добавлена документация для модуля EtherNet/IP Scanner (EtherNet/IP Scanner. Руководство
администратора).
Добавлена документация для модуля IEC-101 Slave (IEC-101 Slave. Руководство администратора).
В документации модуля истории обновлена глава Служебные сигналы (Модуль истории.
Руководство администратора, стр. 18).
Исправлены опечатки.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
65

=== Page 318 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Редакция 5
Обновлена документация для Alpha.Imitator (Alpha.Imitator. Руководство администратора).
В документации модуля SQL Connector в пункте "Соединение с SQL Server 2008 R2" обновлена
строка подключения (Модуль SQL Connector. Руководство администратора, стр. 6).
Исправлены опечатки.
5.13
Улучшения
IEC-104 Master
Поддержаны типы частного диапазона для обмена данными с ПЛК компании "Прософт-
Системы":
151: M_BO_TA_4
156: M_BO_TC_4
153: M_BO_TB_4
154: C_DC_NB_4
150: C_DC_NA_4
IEC-104 Slave
Реализована буферизация изменений исходящих сигналов. Буферизация позволяет
предотвратить потерю изменений при разрывах связи: изменения накапливаются в буфере и
передаются после восстановления связи.
Конфигуратор
Реализована возможность импорта конфигурации в формате *.cfg.
В редакторе адреса для модуля HUB добавлены названия полей.
Модуль истории
Модуль теперь создаёт все директории из пути, указанном в параметре Путь до файла очереди.
Раньше модуль не запускался при отсутствии указанных в пути директорий, поэтому пользователь
должен был создавать все директории самостоятельно.
Modbus TCP Master
При отказе в отправке команды в журнал работы модуля теперь записывается сообщение,
содержащее имя сигнала и причину отказа.
При неудачной попытке установления связи в сообщении журнала работы модуля теперь
указывается не только номер станции, но и адрес канала, по которому не удалось установить
соединение.
SNMP Manager
Добавлено шифрование паролей, используемых модулем при обмене данными по SNMP v1 и
SNMP v2.
Если при получении трапа агент не проходит авторизацию, то:
В журнал работы модуля выводится более информативное сообщение о причине неудачной
авторизации.
В сообщении о неудачной авторизации имя и адрес агента указываются в соответствующих
столбцах. Раньше имя и адрес агента указывались в тексте сообщения.
66
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 319 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
SQL Connector
Параметр Строка подключения разделен на две части: секретная часть и открытая часть. В
секретной части теперь пользователь самостоятельно указывает часть строки подключения,
которая содержит пароль и имя соответствующего атрибута. Раньше пользователь мог указывать
только пароль, а имя соответствующего атрибута подставлял модуль, из-за чего иногда не
удавалось установить соединение с БД.
В секретной части можно указывать и другие части строки подключения, которые пользователь
желает скрыть, например, имя пользователя.
TCP Server
В статистику модуля добавлен параметр Количество подписок на события.
В системном журнале:
устранены лишние сообщения от модуля;
улучшены формулировки некоторых сообщений.
OPC UA Server
Узел, содержащий список публикуемых веток, теперь называется Публикуемые ветки вместо
PublicFolderList.
Изменения
Модуль истории
Для файлов очередей данных по умолчанию теперь используется каталог
C:\Alpha.Server\Queues\ вместо C:\temp\.
TCP Server
Название параметра Анонимные клиенты могут изменять значения сигналов изменено на
Разрешить изменения для анонимных клиентов.
Исправленные ошибки
Модуль истории
При большом количестве БД Alpha.Historian в истории могли отсутствовать некоторые события
из-за того, что модуль выделял фиксированный размер оперативной памяти и её могло не хватать
для передачи данных в Alpha.Historian. Теперь модуль выделяет оперативную память, учитывая
количество БД в конфигурации.
Не создавались директории, указанные в параметре Путь до файла очереди для хранилищ типа
Postgre и HDAServer, если в конце пути отсутствовал разделитель.
IEC-101 Master
Общий опрос и синхронизация времени станций выполнялись даже если соответствующие
интервалы были заданы равными «0».
IEC-101 Slave
Модуль мог не предоставлять значение сигнала, которому была задана Мёртвая зона.
Модуль ошибочно считал недопустимым номер станции больше «254».
Устранено сообщение об ошибке в журнале модуля, которое появлялось при запуске сервера,
если исходящий сигнал не был инициализирован (не имел значения).
Modbus RTU Master
В статистике модуля ошибочно отсутствовал узел Категории данных.
В ОС Linux при разрыве соединения в системном журнале отображалось неинформативное
сообщение.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
67

=== Page 320 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Modbus TCP Master
Устранены возникавшие в некоторых случаях многочисленные пустые "красные" сообщения в
журнале модуля.
В журнале работы модуля при получении ответа-исключения с некоторыми кодами неверно
указывалась причина разрыва связи.
OPC DA Client
При переименовании группы серверов служебный сигнал «HasActiveServer» размещался в
папке со старым названием группы.
SnapShot
Неверно восстанавливались большие значения сигнала типа Uint8.
SNMP Manager
При разрыве связи по активному каналу качество входящего сигнала становилось плохим, даже
если переход на резервный канал выполнялся до истечения таймаута потери связи по каналу.
Параметр конфигурации Агент включен в статистике модуля назывался Состояние агента.
Теперь параметр в конфигурации и в статистике называется одинаково.
Иногда модуль мог не принимать некоторые трапы.
SQL Connector
Иногда служба Alpha.Server не останавливалась при наличии в конфигурации модуля SQL
Connector.
OPC UA Server
Для некоторых клиентов некорректно отображалась статистика модуля в приложениях
Конфигуратор и Статистика.
Конфигурация модуля запрещала клиенту изменять значение сигнала, но атрибут
«UserAccessLevel» соответствующего сигналу узла ошибочно отражал возможность изменения.
Конфигуратор
Работа приложения завершалась с ошибкой при попытке добавления папке свойства 2(Value)
или 5002(RawValue).
В редакторе адреса для модуля OPC UA Client ширина поля Идентификатор узла была
фиксированной. Теперь ширина поля изменяется автоматически в зависимости от длины вводимого
значения.
Дерево модулей сворачивалось при блокировке конфигурации, если был выделен узел модуля
истории.
Просмотрщик лога кадров
При просмотре журналов работы модулей Modbus могло появляться сообщение об ошибке в
случае, если для входящего кадра отсутствовал соответствующий исходящий кадр. Теперь
входящий кадр отображается без появления сообщения об ошибке, даже если в журнале
отсутствует соответствующий исходящий кадр.
5.13.1
Улучшение
SQL Connector
Реализована возможность выполнения нескольких взаимосвязанных запросов в одной сессии.
Исправленные ошибки
68
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 321 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
SQL Connector
При использовании ODBC запросы к источнику переставали выполняться после перезапуска
PostgreSQL.
В Конфигураторе возникала ошибка с сообщением о неизвестном узле при загрузке
конфигурации, созданной в Alpha.Server до версии 5.10.0.
Siemens S7 Client
Связь с ПЛК могла восcтанавливаться долго при нестабильном соединении.
5.13.2
Улучшение
Alpha.Imitator
Улучшена обработка длительных вычислений в режиме перезаписи значений.
5.13.3
Улучшение
Modbus TCP Master
Реализован обмен данными со шлюзом RTU-TCP, который является станцией Modbus TCP с
фиксированным номером «255».
5.13.4
Исправленная ошибка
OPC UA Client
Alpha.Server зависал при инициализации модуля, если сертификат модуля был
недействительным.
5.13.5
Исправленные ошибки
Alpha.Server
Alpha.Server прекращал работу при запуске, если в проекте Alpha.DevStudio были неверно
настроены обработчики, генерирующие сообщения для событий.
Alpha.Imitator
Результат имитации в режиме перезаписи истории мог оказаться неверным, если метка времени
действительного значения не совпадала с временем начала интервала имитации.
Добавлены изменения Alpha.Server 5.12.31
Исправленная ошибка модуля истории
Устранена проблема, из-за которой Alpha.HMI мог не строить график истории значений при
большом объёме данных в БД PostgreSQL.
5.13.6
Исправленные ошибки
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
69

=== Page 322 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Alpha.Imitator
В режиме перезаписи истории результат повторной имитации был неверным.
OPC AE Server, OPC DA Server
Иногда модули могли не запускаться.
Модуль истории
Исправлены ошибки в статистике модуля:
В статистике хранилища Postgre параметр Состояние ошибочно отображал информацию об
ошибке соединения, а параметр Ошибка соединения отображал информацию о состоянии
подключения.
В названии узла хранилища для сохранения значений удалена лишняя надпись «(сохранение
событий)».
5.13.7
Исправленные ошибки
SQL Connector
При запросе значений более одного столбца, значения могли не записываться в сигналы.
При ошибке выполнения запроса модуль не выводил сообщение об ошибке и не устанавливал
сигналу плохое качество.
Modbus TCP Master
Исправлена ошибка модуля Modbus TCP Master, из-за которой мог долго выполняться
резервный переход Alpha.Server.
5.13.8
Исправленная ошибка
Alpha.Imitator
После перезаписи истории скорректированное значение не использовалось в вычислениях.
Добавлены изменения Alpha.Server 5.12.33
Улучшение Модуля рассылки сообщений SMTP
Время генерации событий в сообщениях теперь указывается в часовом поясе, заданном для
получателя.
5.13.9
Исправленная ошибка
Модуль истории
Не удавалось получить историю событий из БД PostgreSQL.
5.13.10
Исправленная ошибка
Alpha.Imitator
Иногда Alpha.Imitator не восстанавливал историю значений некоторых сигналов в режиме
"Дополнение пропущенных исторических данных" (Backfilling).
70
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 323 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
5.13.11
Исправленная ошибка
OPC UA Client
Иногда обмен данными с ПЛК мог прекращаться.
5.12
Новые возможности
Реализованы новые модули:
BACnet Client, с помощью которого Alpha.Server может обмениваться данными с устройствами,
поддерживающими протокол BACnet.
DTS Client, с помощью которого Alpha.Server может обмениваться данными с подсистемой
передачи данных "Портал" (АО "РАСУ").
IEC-61850 Client
При установлении связи с устройством теперь однократно выполняется общий опрос для
получения актуальных значений параметров, которые изменяются редко. Раньше модуль получал
значения этих параметров только после их изменения в устройстве.
Модуль истории
Периодическое повторное сохранение последней записи для сигналов, значения которых изменяются
редко. Настраивается для сигнала в свойстве 9002 в виде строки со значениями параметров:
{ ServerTime = (1) EnableRepeatedWrites = (1) RepeatTimeout = (t)}
где «t» – период в секундах, по истечении которого производится повторное сохранение последней записи
по сигналу.
Исправленные ошибки
OPC AE Server
Свойство 999003 (EventsEnabled) со значением «False» ошибочно не блокировало генерацию
событий.
При предоставлении информации о событиях в виде значений служебных сигналов:
В некоторых случаях служебный сигнал «Acknowledged» квитированного события ошибочно
имел значение «False» вместо «True».
При блокировании через служебный сигнал «Enabled.Set», блокированный источник не
отображался в списке Подавления и блокировки в Alpha.Alarms.
SnapShot
Служебные сигналы управления загрузкой/генерацией/восстановлением файлов-срезов
ошибочно создавались в папке «Service.Modules.SnapShot Module», вместо папки
«Service.Modules.<Имя модуля>», при изменении имени модуля в конфигурации.
Файлы-срезы ошибочно создавались с расширением *.xml, вместо расширения, указанного в
служебном сигнале «OutFileName».
Иногда файлы-срезы могли создаваться с неверным именем в неверном каталоге.
IEC-104 Master
Ошибочно не принимались на обслуживание сигналы, значения которых передавались как
отдельные биты одного и того же адреса.
В редакторе адреса ошибочно было доступно поле Мёртвая зона.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
71

=== Page 324 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
IEC Slave
Для некоторых протокольных типов не учитывалось значение параметра Мертвая зона, заданное
в адресе сигнала.
Modbus RTU Master
В Конфигураторе не удавалось изменить имя категории данных.
Просмотрщик лога кадров
Возникала ошибка при попытке фильтрации записей по имени группы серверов в журналах
модулей OPC DA Client и OPC UA Client.
Управляющий
В редких случаях не выполнялась синхронизация конфигураций.
Конфигуратор
Работа приложения завершалась с ошибкой при редактировании адреса сигнала, если адрес
ссылался на несуществующий модуль Modbus RTU Master, Modbus RTU Slave, Modbus TCP
Master или Modbus TCP Slave.
Прочие изменения
Modbus TCP Slave
Из журнала работы модуля удалены столбцы Первый адрес, Последний адрес и Количество
элементов.
OPC UA Client
Имя сигнала, которому не удалось подписаться на узел UA сервера, теперь указывается в
сообщении о неудачной подписке в журнале приложений. Раньше в сообщении указывался только
идентификатор узла UA сервера.
Конфигуратор, журналы работы модулей
Исправлены ошибки и опечатки в названиях и описаниях параметров, в сообщениях журналов
работы модулей.
5.12.1
Исправленная ошибка
Модуль истории
В ОС Linux модуль не сохранял данные в БД PostgreSQL.
5.12.2
Исправленные ошибки
OPC UA Client
Alpha.Server прекращал работу:
если модулю OPC UA Client был задан контрольный узел, значение которого невозможно
преобразовать в 8-байтное целое со знаком (int64).
в редких случаях при остановке модуля OPC UA Client.
5.12.3
Исправленная ошибка
72
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 325 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
OPC UA Client
Alpha.Server прекращал работу, если модулю OPC UA Client был задан контрольный узел,
отсутствующий в UA сервере.
5.12.4
Улучшение
IEC-61850 Client
Поддержано получение данных класса MV (измеряемые значения). Для получения данных
используется протокольный тип IN_FLOAT32_MV.
Исправленные ошибки
Модуль истории
В редких случаях Alpha.Server прекращал работу при остановке модуля истории.
Alpha.Imitator прекращал работу при запуске модуля истории.
IEC-61850 Client
Модуль не получал данные отчётами, если набор данных содержал хотя бы один объект данных,
находящийся в разных логических устройствах с блоком управления отчётами.
5.12.6
Улучшения
Alpha.Imitator
Теперь Alpha.Imitator работает в ОС семейства Linux.
Статистика
Реализовано сохранение статистики в файл через интерфейс командной строки (CLI). Для
сохранения в файл Статистика запускается из командной строки с параметрами:
AlphaStatistics.exe save --host HOST --port PORT --output-file OUTPUT-FILE
где:
HOST - адрес источника статистики;
PORT - порт источника статистики;
OUTPUT-FILE - полный путь к выходному файлу статистики формата *.stat.
Исправленная ошибка
Модуль истории
Alpha.Server прекращал работу при попытке записи события в БД PostgreSQL, если БД была
создана скриптом из версий Alpha.Server до 5.10.5.
Изменение
Alpha.Server
В ОС семейства Linux имя сервиса теперь - alpha.server.
Для корректной работы модулей History Module и SQL Connector Module с источниками данных
необходимо указать переменные среды сервису alpha.server:
1. Откройте unit-файл сервиса alpha.server командой:
sudo systemctl edit alpha.server
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
73

=== Page 326 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
2. В открывшемся редакторе пропишите сервису переменные среды в разделе Service:
Environment=ODBCSYSINI=/etc
3. Сохраните изменения и перезапустите сервис alpha.server командой:
sudo systemctl restart alpha.server
5.12.7
Новая возможность
Реализован новый модуль Siemens S7 Client, с помощью которого Alpha.Server может
обмениваться данными с контроллерами Siemens (S7).
Изменение
Alpha.Imitator
В ОС семейства Linux имя сервиса теперь - alpha.imitator.
Исправленная ошибка
NetDiag2
В ОС семейства Linux отключение сетевого интерфейса приводило к повышению загрузки ЦП.
5.12.8
Исправленная ошибка
IEC-104 Master
Иногда модуль ошибочно игнорировал значения с меткой времени, полученные общим опросом.
5.12.9
Улучшения
IEC-61850 Client
Поддержано получение данных типа INT64 и класса BCR (считывание показаний двоичного
счётчика). Для получения данных используются протокольные типы IN_INT64 и IN_INT64_BCR.
IEC-104 Slave
Теперь модуль отправляет кадр окончания общего опроса.
Modbus TCP Master
Модуль может использовать одно TCP-соединение для опроса всех станций с одинаковым IP-
адресом. Для этого параметру модуля Использовать одно TCP соединение на несколько станций
установите значение «Да».
Исправленные ошибки
IEC-61850 Client
Ошибочно отбрасывались некоторые значения некоторых типов.
74
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 327 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
5.12.10
Исправленные ошибки
Siemens S7 Client
Устранена высокая загрузка ЦП при работе модуля.
Устранены частые сообщения об ошибках получения статуса.
Alpha.Server
Иногда Alpha.Server не мог получить лицензии при использовании программного ключа Sentinel
(HASP).
В ОС Linux скрипт создания БД PostgreSQL ошибочно назывался alpha.postgresql.9.5.sql.
Теперь имя скрипта - postgresql.9.5.sql.
В Программах и компонентах отображалась неактуальная контактная информация (сайт и
телефон техподдержки).
Сервисные приложения
В Диспетчере задач некорректно отображались имена сервисных приложений.
В редких случаях в Конфигураторе возникала ошибка при попытке открыть Редактор адреса.
5.12.11
Исправленные ошибки
Modbus TCP Master
Иногда Alpha.Server прекращал работу при запуске в резерве.
Siemens S7 Client
Устранена задержка при записи значений в ПЛК.
IEC-61850 Client
Устранена задержка получения данных при использовании большого количества блоков
управления отчетами.
5.12.12
Улучшение
IEC-61850 Client
Поддержана отправка данных класса ASG (задание значения аналогового сигнала). Для отправки
данных используется протокольный тип OUT_ASG.
Исправленные ошибки
Siemens S7 Client
После запуска Alpha.Server опрос категорий данных начинался с задержкой, равной интервалу
опроса категории. Теперь категории данных опрашиваются сразу после запуска Alpha.Server.
Устранена высокая загрузка ЦП при работе модуля.
Устранен длительный опрос ПЛК.
Modbus TCP Master
При использовании одного канала связи для опроса нескольких станций разрывалось
соединение со всеми станциями, если терялась связь с одной из них. Теперь при потере связи или
возникновении ошибок с одной из станций, для других станций соединение не разрывается.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
75

=== Page 328 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
5.12.13
Исправленные ошибки
OPC UA Server
В ОС Linux Alpha.Server прекращал работу при перезапуске модуля с помощью сервисного
сигнала «Active.Set».
Alpha.Imitator
Alpha.Imitator зависал после запуска сессии перезаписи.
Modbus TCP Master
Соединение со станцией разрывалось прежде, чем истечет таймаут по 5 запросам, ожидающим
ответ.
В журнале работы модуля некорректно отображался номер станции.
5.12.14
Исправленные ошибки
Modbus TCP Master
Модуль переставал получать значения из области данных после получения некорректного кадра
из этой области.
Siemens S7 Client
Некорректно выполнялась запись данных типа Bool в биты переменной ПЛК.
Иногда Alpha.Server останавливался в течение длительного времени из-за долгой остановки
модуля Siemens S7 Client.
5.12.15
Улучшение
Modbus TCP Slave
Реализовано предоставление значений сигналов типа Double. Для предоставления данных
используется протокольный тип TMF8.
Исправленная ошибка
Alpha.Imitator
Не выполнялась перезапись значений сигналов, которым была задана зона нечувствительности
по значению при сохранении в историю.
5.12.16
Исправленная ошибка
IEC-61850 Client
Alpha.Server прекращал работу при разрыве связи с устройством.
5.12.17
Исправленная ошибка
76
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 329 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
SQL Connector
В ОС Ubuntu 22.04.1 LTS Alpha.Server прекращал работу при попытке запроса к Microsoft SQL
Server 2008 R2 (SP1) через ODBC Driver 18 for SQL Server.
5.12.18
Исправленные ошибки
Дистрибутив Alpha.Server
В ОС Astra Linux в некоторых случаях при установке дистрибутива не создавались сертификаты
и конфигурационный файл *.xml, из-за чего Alpha.Server не запускался.
Модуль истории
Не удавалось получить историю, либо получение истории выполнялось долго, если
отсутствовала связь с некоторыми БД.
5.12.19
Исправленная ошибка
IEC-61850 Client
Модуль не получал данные отчётами, у которых отсутствовало поле ReasonForInclusion.
5.12.20
Улучшение
Modbus TCP Master
Поддержан протокол Modbus RTU over TCP/IP. Для обмена данными по протоколу Modbus RTU
over TCP/IP параметру модуля Формат кадров установите значение «RTU».
Исправленная ошибка
Modbus TCP Master
При опросе нескольких станций модуль мог несвоевременно опрашивать некоторые из них.
5.12.21
Улучшение
Modbus TCP Master, Modbus TCP Slave
Реализован обмен данными типов Int8, Uint8. Для обмена данными используются протокольные
типы TM8, TM8_TIME (Slave →Master) и TR8, TR8_TIME (Master →Slave).
Исправленные ошибки
IEC-61850 Client
Alpha.Server долго останавливался при наличии в конфигурации модуля большого числа блоков
отчётов.
5.12.22
Исправленные ошибки
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
77

=== Page 330 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
IEC-61850 Client
Alpha.Server прекращал работу при разрыве соединения с устройством во время обработки
отчёта.
Modbus TCP Master
После запуска Alpha.Server опрос категорий данных начинался с задержкой, равной интервалу
опроса категории. Теперь категории данных опрашиваются сразу после запуска Alpha.Server.
Не изменялось значение служебного сигнала «Station <N>.ConnectionState», когда станция
переставала отвечать на запросы.
5.12.23
Улучшение
IEC-61850 Client
Для блока управления отчётом теперь можно указывать события, по которым будет
генерироваться отчёт.
5.12.24
Улучшение
Siemens S7 Client
Реализована возможность указывать тип соединения (Connection Resource) в настройках канала.
Исправленные ошибки
Siemens S7 Client
Иногда при обмене данными соединение с ПЛК разрывалось.
Устранены сообщения об ошибках получения статуса ПЛК в журнале работы модуля.
В редких случаях некорректно принимались данные типа WORD и DWORD.
Alpha.Server долго перезапускался при большом количестве устройств в конфигурации модуля.
Область памяти ПЛК MB (Merkers) опрашивалась некорректно.
Изменение
Siemens S7 Client
Настройка периода запросов статуса ПЛК больше не требуется, соответствующий параметр
удалён из настроек конфигурации модуля.
5.12.25
Улучшение
Модуль истории
Реализованы служебные сигналы модуля, отображающие:
состояние связи с БД Alpha.Historian;
размер очереди на запись в БД Alpha.Historian.
Исправленные ошибки
Alpha.Imitator
Модуль истории не инициализировался при запуске Alpha.Imitator.
78
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 331 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
NetDiag2
В ОС Linux модуль не запускался при работе Alpha.Server из-под непривилегированной учётной
записи.
5.12.26
Исправленная ошибка
IEC-104 Master
Устранена проблема, из-за которой Alpha.Server иногда мог прекращать работу.
5.12.27
Исправленные ошибки
IEC-61850 Client
Устранена проблема, из-за которой Alpha.Server иногда мог прекращать работу.
NetDiag2
В ОС Linux Alpha.Server прекращал работу при отключении сетевого адаптера.
Изменение
Обновлены иконки сервисного приложения Статистика.
5.12.28
Исправленная ошибка
OPC UA Client
Модуль не подключался к некоторым UA серверам.
5.12.29
Исправленная ошибка
OPC UA Server, SNMP Manager
Alpha.Server не выполнял обмен данными по OPC UA и SMNP при большом количестве
опрашиваемых станций Modbus TCP.
5.12.30
Исправленная ошибка
Модуль истории
Запрос истории значений из БД PostgreSQL прекращался при большом количестве сохраненных
в БД значений сигнала.
5.12.31
Исправленная ошибка
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
79

=== Page 332 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Модуль истории
Устранена проблема, из-за которой Alpha.HMI мог не строить график истории значений при
большом объёме данных в БД PostgreSQL.
5.12.32
Исправленная ошибка
OPC AE Server, OPC DA Server
Иногда модули могли не запускаться.
5.12.33
Улучшение
Модуль рассылки сообщений SMTP
Время генерации событий в сообщениях теперь указывается в часовом поясе, заданном для
получателя.
Изменения документации
Редакция 1
Изменены имена сервисов в ОС Linux для Alpha.Server и Alpha.AccessPoint.
Исправлены пути установки Alpha.Server и расположения журналов модулей в ОС Linux.
В документе на Модуль истории в приложении Установка и настройка PostgreSQL обновлена
информация по запуску скрипта postgresql.9.5.sql в ОС Linux (Модуль истории. Руководство
администратора стр. 28).
Некоторые скриншоты файлов конфигураций заменены на текстовые блоки кода, а в веб-версии
документации таким блокам кода добавлена подсветка синтаксиса.
Исправлены опечатки.
Редакция 2
Модуль истории. Руководство администратора
Добавлена информация по настройке переменных среды сервису alpha.server в ОС Linux (стр.
30).
Alpha.Server. Руководство администратора
Добавлено описание качества WAITING_FOR_INITIAL_DATA (32) (стр. 41).
Редакция 3
Добавлена документация для модулей:
BACnet Client. Руководство администратора
DTS Client. Руководство администратора
80
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 333 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Редакция 4
Добавлена документация для модуля Siemens S7 Client. Руководство администратора.
Редакция 5

Модуль истории. Руководство администратора
Глава "Конфигурирование сигналов" заменена на главы Сохранение истории значений сигналов и
Дополнительные параметры сохранения истории (стр. 14).
В главу Дополнительные параметры сохранения истории добавлено описание настройки
периодического повторного сохранения последней записи сигнала (стр. 16).
Обновлены картинки в приложении Установка и настройка PostgreSQL (стр. 26).
В подразделе Указание переменных среды сервису alpha.server в пункте 2 обновлен блок кода
(стр. 32).
Обновлён раздел Диагностика работы (стр. 18).
Модуль SQL Connector. Руководство администратора
В подразделе Указание переменных среды сервису alpha.server в пункте 2 обновлен блок кода
(стр. 29).
В документации модулей Data Buffer, FS Generator, NetDiag, NetDiag2 обновлёны разделы
"Диагностика работы"
OPC DA Client Модуль OPC DA Client. Руководство администратора
В разделе Проверка состояния соединения с сервером-источником обновлены картинки (стр. 16).
В документации Alpha.AccessPoint обновлены устаревшие картинки.
Исправлены опечатки.
Редакция 6
Alpha.Server. Руководство администратора
Добавлено описание качества CALCULATED (200) (стр. 40).
Модуль логики. Руководство администратора
Добавлено описание параметра Стратегия приведения целочисленных типов при
использовании арифметических операторов (стр. 6).
Модуль OPC UA Server. Руководство администратора
Добавлены параметры OPC UA Server, необходимые клиентам для подключения (стр. 4).
Добавлено описание настройки модуля в Alpha.DevStudio (стр. 5).
Добавлено описание настройки ограничения доступа к данным по OPC UA в Alpha.DevStudio (стр.
10) и Конфигураторе (стр. 16).
Добавлена информация о расположении сертификатов OPC UA Server в OC Linux (стр. 23).
Обновлена глава Работа с клиентскими сертификатами (стр. 23).
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
81

=== Page 334 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Модуль OPC UA Client. Руководство администратора
Добавлен раздел Настройка обмена данными с OPC UA сервером, в котором (стр. 6):
добавлено описание настройки модуля в Alpha.DevStudio (стр. 7);
главы по настройке модуля через Конфигуратор обновлены и объединены в главу
Настройка в Конфигураторе (стр. 29).
Добавлено описание настройки получения значений сигналов по команде в Alpha.DevStudio (стр.
26) и Конфигураторе (стр. 37, 41).
Добавлена информация о расположении сертификатов OPC UA Client в OC Linux (стр. 47).
Обновлена глава Установка безопасного соединения (стр. 47).
Добавлена глава Контроль обмена данными (стр. 50).
Добавлено описание служебных сигналов опроса групп чтения (стр. 52).
Исправлены опечатки и обновлены некоторые рисунки.
5.11
Улучшения
Модуль истории
База данных PostgreSQL теперь может использоваться модулем не только для сохранения
значений, но и для сохранения истории событий, а также чтения истории значений и событий.
Modbus TCP Master
Категории данных могут опрашиваться не только периодически, но и по команде пользователя.
Опрос по команде позволяет получать данные, например, только при открытии некоторого экрана в
Alpha.HMI.
Реализован служебный сигнал «Status», отображающий текущее состояние опроса категории
данных по команде пользователя.
OPC AE Server
Из нескольких событий с одинаковым источником, условием и временем активации квитируется
только одно событие, выбранное пользователем. Раньше квитировались все такие события при
квитировании одного из них.
Квитирование события возможно даже после отключения генерации событий по
соответствующему условию.
IEC-61850 Client
Журнал работы модуля стал информативнее. Данные, принятые отчётами, отображаются в окне
расшифровки кадров.
IEC 104 Master
При потере связи со станцией модуль может предпринимать попытки восстановления связи
через интервал времени, заданный в параметре Задержка между попытками подключения. Задержка
между попытками подключения нужна в случаях, когда опрашиваемая станция не может быстро
реагировать на потерю связи и не позволяет IEC 104 Master быстро восстановить соединение.
Modbus RTU Slave
В параметре Задержка перед отправкой ответа теперь можно задавать интервал времени, через
который будет отправляться ответ на запрос. Раньше задержка была фиксированная и составляла
50 мс.
TCP Server
Функции API сервера стали доступны по TCP. При наличии в конфигурации модуля TCP Server в
адресном пространстве сервера теперь присутствует сигнал «Service.InvokeFromJSON». Раньше
сигнал присутствовал только при наличии в конфигурации модуля OPC DA Server.
82
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 335 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Alpha.Imitator
Поддержаны новые режимы работы:
режим коррекции исторических данных, которой позволяет выполнять пересчёт записанных
в историю значений и их перезапись в историю с теми же метками времени;
режим дополнения пропущенных исторических данных, который позволяет на основе файлов
данных записывать в историю пропущенные значения.
Исправленные ошибки
Alpha.Server
Alpha.Server прекращал работу, если корневому узлу дерева сигналов в свойстве 999000
(ObjectType) был задан тип объекта, который не описан в файле с внешними объектами
Alpha.ServerExternalObjects.xml или в свойствах сигналов.
В редких случаях Alpha.Server зависал в процессе остановки модуля истории.
Alpha.AccessPoint
В редких случаях Alpha.AccessPoint:
переставал получать данные от Alpha.Server;
зависал в процессе остановки модуля истории.
Modbus RTU Slave, Modbus TCP Slave
Не все пересечения областей данных сигналов обнаруживались модулями.
Сигналам могли неверно выставляться значения, полученные функциями «6 (0x10) Write
Multiple registers» и «23 (0x17) Read/Write Multiple registers».
Модули переставали отвечать на запросы после получения некорректного запроса функциями «6
(0x10) Write Multiple registers» или «23 (0x17) Read/Write Multiple registers».
При запросе нескольких регистров функциями «03 (0x03) Read Holding Registers» и «04
(0x04) Read Input Registers» модули отправляли ответ, сформированный некорректно.
Modbus TCP Master
При разрыве связи модуль устанавливал плохое качество входящим сигналам до того, как
истекал таймаут потери связи.
Modbus RTU Master
Модуль отправлял подчиненной станции команды, даже если их качество было плохим.
После резервного перехода:
в статистике модуля отображалась неверная информация о количестве обслуживаемых
сигналов;
модуль прекращал опрос станций.
Modbus TCP Slave
Поля Последний адрес и Количество элементов журнала работы модуля заполнялись
некорректно при получении запроса функцией «06 (0x06) Write Single Register».
TCP Server
В редких случаях журнал работы модуля не открывался в приложении Просмотрщик лога
кадров.
IEC-101 Master
При попытке открыть статистику COM-портов модуля возникала ошибка, если в имени COM-
порта встречался символ точки.
SNMP Manager
В редких случаях в журнале работы модуля не отображались IP адреса в колонках Удаленный
адрес и Локальный адрес.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
83

=== Page 336 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
OPC AE Server
События, измененные с помощью вычислений (свойство 777013):
могли не передаваться по OPC DA;
не квитировались, если были изменены условие или подусловие.
События, запрошенные с помощью функции «Refresh», не обрабатывались модулем логики.
5.11.1
Улучшение
OPC UA
Появилась возможность указывать какие из веток дерева сигналов Alpha.Server будут
доступны UA клиентам и смогут ли клиенты изменять значения сигналов в доступных ветках. Это
позволяет ограничить доступ к сигналам Alpha.Server по OPC UA.
Например, к Alpha.Server одновременно подключены DA и UA клиенты. DA клиенту доступны все
сигналы дерева, возможно изменение значений всех сигналов. UA клиенту доступны только
некоторые ветки дерева сигналов, возможно изменение значений сигналов только в некоторых из
доступных веток.
5.11.2
Исправленная ошибка
SNMP Manager
Для подключения к агенту модуль использовал порт «161», даже если в конфигурации в
параметре Порт для опроса был задан другой порт.
5.11.4
Исправленная ошибка
OPC UA Client
Устранена проблема, из-за которой Alpha.Server мог зависать при остановке.
5.11.5
Исправленная ошибка
Модуль резервирования
Alpha.Server прекращал работу в ОС Astra Linux 1.7, Red OS 7.1 или Red OS 7.3.
5.11.6
Исправленная ошибка
SNMP Manager
Иногда служебный сигнал «Active» активного канала ошибочно принимал значение «False»
вместо «True».
Активным называется канал, который в данный момент используется для обмена данными с
агентом. Служебный сигнал «Active» этого канала должен иметь значение «True».
84
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 337 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
5.11.7
Исправленная ошибка
OPC UA Client
Модуль переставал получать данные от некоторых UA серверов после их аварийного
перезапуска.
5.11.8
Исправленные ошибки
NetDiag2
Отключение сетевого интерфейса приводило к повышению загрузки ЦП.
SNMP Manager
Случаи аварийного завершения работы Alpha.Server при наличии в конфигурации модуля SNMP
Manager.
5.11.9
Исправленные ошибки
OPC UA
Не соответствовала требованиям спецификации OPC UA информация о UA сервере,
предоставляемая узлами «ServerStatus» и «BuildInfo».
SNMP Manager
Модуль не получал данные от агента, который использовал пароль, содержащий символы
Кириллицы или некоторые специальные символы.
5.11.10
Новые возможности
Modbus TCP Master
Модуль теперь умеет определять активное устройство (в группе резервируемых устройств) на
основе ответов устройств. Устройство, которое ответило исключением, модуль считает
находящимся в резерве и отправляет запрос другому (активному) устройству группы.
Изменения
Modbus TCP Master
Для того, чтобы выбор активного устройства выполнялся правильно, изменена схема
конфигурации модуля. Теперь внутри узла «Станция» можно явно указать все резервируемые
устройства и каналы связи с каждым устройством.
5.11.11
Исправленные ошибки
Modbus TCP Master
Иногда при использовании версии 5.11.10 возникали проблемы при опросе подчиненных станций
и опрос велся не по всем указанным в конфигурации адресам.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
85

=== Page 338 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
5.11.12
Исправленная ошибка
Modbus TCP Master
Alpha.Server зависал при разрывах связи с подчиненной станцией.
Изменения документации
Редакция 2
Alpha.Imitator. Руководство администратора
Добавлен раздел Настройка в Alpha.DevStudio (стр. 7).
Скриншоты файлов конфигураций заменены на текстовые блоки кода.
Обновлена структура и содержимое документа.
5.10
Улучшения
Alpha.Server
Длительность хранения резервных копий конфигурации сервера, задаваемая в параметре
StorageDepth, ограничена интервалом от «0» до «90» дней.
Если объекту в свойстве 999000 (ObjectType) был задан тип, который не описан в файле с
внешними объектами Alpha.ServerExternalObjects.xml, то Alpha.Server прекращал работу, а
сообщение в журнале приложений не описывало причину сбоя. Теперь текст сообщения содержит
имя узла и тип объекта, которые стали причиной сбоя.
Если в ОС Linux модулям сервера требовалось открывать более 340 сетевых соединений, то не
все модули могли открыть соединения и успешно работать. Теперь сервер по умолчанию может
успешно открыть порядка 3 тысяч соединений.
SQL Connector
Пароль для строки подключения задаётся в отдельном параметре и хранится в конфигурации в
зашифрованном виде.
IEC-104 Master, IEC Slave
Максимальная длина строки, которую можно передать с использованием типов U-MON и U-
CTRL, составляет 220 символов.
SNMP Manager
Улучшен журнал работы модуля:
Поле Тип отображается только для входящего кадра, и отсутствует для исходящего.
В поле Тип отображается тип данных SNMP.
Если получен неподдерживаемый тип данных, то в поле Значение записывается значение
«Bad Type», а в поле Тип значение «Undefined».
Если тип PDU не соответствует типу сигнала в сервере, то в поле Значение записывается
значение «Bad Type», а в поле Тип значение «Тип из PDU».
Во входящих кадрах отображались только те значения OID, которые были записаны в
сигнал. Теперь входящий кадр отображает все полученные значения OID, даже если они не
изменились.
Для входящих и исходящих кадров исключены поля Метка времени и Качество.
86
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 339 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Исправленные ошибки
SQL Connector
Пароль строки подключения попадал в сообщения журнала приложений.
Конфигуратор
Сбой при редактировании адреса сигнала, если адрес ссылался на несуществующий модуль
Modbus RTU Master, Modbus RTU Slave, Modbus TCP Master или Modbus TCP Slave.
Было невозможно настроить адрес сигнала для модуля OPC HDA Client.
В окне Изменение свойства блокировались поля Значение и Тип при изменении номера свойства.
Просмотрщик лога кадров
Позиция горизонтального скролла сбрасывалась в момент появления в журнале модуля новой
записи.
Сообщения об ошибках отображались в виде отдельных окон, после чего приложение зависало.
Modbus RTU Master
Адреса регистров входящих кадров некоторых функций в журнале модуля отображались
некорректно.
Modbus TCP Slave, Modbus RTU Slave
Сигналы модулей с адресом «65535» не получали значения, переданные функцией 16 (0х10).
В журналах работы модулей область расшифровки кадров функции 6 (0х06) была пустой.
NetDiag2
Параметру Период диагностики TraceRoute устанавливалось значение параметра Период
диагностики Ping.
SNMP Manager
В ОС Linux при записи в сигнал значения, максимального для типа Counter64, фактически
записывалось значение, максимальное для типа Counter32.
При запросе элементов массива модуль мог потреблять большой объем памяти.
Вместо запроса отдельных элементов массива запрашивался весь массив.
IEC-61850 Client
В статистике каналов и отчётов модуля время отображалось некорректно.
OPC AE Server
Находясь в резерве, модуль слал клиентам события, не требующие квитирования.
В некоторых случаях события по условию «Deviation» могли генерироваться неверно.
Alpha.AccessPoint
Некоторые сообщения HUB модуля отображались с неверной кодировкой.
5.10.1
Улучшение
Logics Module
Теперь сообщается не только об обнаружении цикла в вычислениях, но и перечисляются узлы,
образующие цикл.
5.10.2
Исправленные ошибки
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
87

=== Page 340 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
SQL Connector
Выполнение SQL запроса с помощью сигнала MakeQuery_Command могло замедлять выполнение
вычислений в случаях, когда SQL запрос выполнялся длительное время или выполнялся часто.
SQL запрос выполнялся даже при плохом качестве сигнала MakeQuery_Command. Теперь если
сигнал MakeQuery_Command имеет плохое качество, то SQL запрос не выполняется.
IEC-104 Master
При использовании для подачи команды процедуры предварительного выбора модуль мог
ошибочно отправить команду исполнения несколько раз вместо одного. Проблема наблюдалась при
использовании ПЛК REGUL R500.
5.10.4
Улучшение
SNMP Manager
Для проверки наличия связи с SNMP агентом модуль отправляет тестовый запрос с OID, равным
«0». Однако некоторые SNMP агенты не могут отвечать на такой запрос. Теперь в параметре OID для
тестового запроса можно задавать OID, который будет использоваться модулем для проверки
наличия связи с SNMP агентом. Пустое значение параметра соответствует OID, равному «0».
5.10.5
Улучшение
OPC UA Client
Появилась возможность чтения значений группы сигналов по команде.
5.10.6
Изменение
OPC UA Client
Количество OPC UA серверов, к которым может единовременно подключиться OPC UA Client
одного экземпляра Alpha.Server, увеличено со 100 до 200.
Изменения документации
Редакция 1
Добавлена документация для модуля TEM-104 Модуль ТЭМ-104. Руководство администратора.
Модуль Modbus RTU Master. Руководство администратора
Добавлен раздел Обмен данными по протоколу Modbus с описанием функций протокола Modbus,
поддерживаемых модулем (стр. 6).
В раздел Журнал работы модуля добавлено описание кадров данных (стр. 34).
Объединены в главу Диагностика работы модуля разделы с описанием служебных сигналов,
статистики и журнала работы модуля (стр. 31).
88
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 341 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Модуль SQL Connector. Руководство администратора
Добавлено описание параметра Пароль (стр. 6).
Примеры строк подключения в виде скриншотов заменены на текстовые поля.
Модуль SNMP Manager. Руководство администратора
Добавлено описание параметра OID для тестового запроса (стр. 13).
Добавлен раздел Служебные сигналы (стр. 19).
Модуль OPC AE Server. Руководство администратора
Добавлен раздел "Блокирование и подавление" (стр. 13).
Добавлено описание параметров Правило обработки подавленных событий и Отсылать
квитирование по подавленным источникам (стр. 15).
Обновлен раздел Передача событий по OPC DA (стр. 26).
Обновлен раздел Диагностика работы модуля (стр. 36).
Alpha.Server. Руководство администратора
В таблицу свойств сигналов добавлены свойства 777001-777003, 777020-777051 (стр. 38, 39).
Добавлен диапазон допустимых значений атрибута StorageDepth (стр. 36).
Подсистема резервирования. Руководство администратора
В описании атрибута Port исправлено имя файла конфигурации (стр. 13).
5.9
Новые возможности
Модуль FINS Client, предназначенный для обмена данными по протоколу FINS.
OPC AE Server
Возможность рассылки уведомлений о квитировании событий по подавленным источникам.
Улучшения
TCP Server Module
Теперь клиенты TCP Server могут обращаться к сигналам по ссылкам, определенным в
свойствах 6001-6004.
Alpha.Server
Теперь при установке сервера не отображаются терминальные окна.
Исправленные ошибки
Logics Module
Не выполнялись вычисления для сигналов, которые являлись объектами.
Alpha.Server
В ОС Linux резервное копирование конфигурации сервера выполнялось по времени UTC вместо
локального времени.
OPC AE Server
Устранена проблема, из-за которой в Alpha.Alarms добавление нового комментария после
квитирования не являлось событием.
5.9.1
Исправленная ошибка
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
89

=== Page 342 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
OPC UA Client
Модуль не мог подписаться на узел UA-сервера с типом идентификатора «opaque».
5.9.2
Исправленная ошибка
Alpha.Imitator
Не загружались данные из имитационной БД.
5.9.3
Улучшение
Logics Module
Теперь в настройках модуля в параметре Стратегия приведения целочисленных типов при
использовании арифметических операторов можно выбирать правило вывода типов результатов
арифметических операций. Возможные значения:
«Все уровни» - результатом может быть целое число размером «1», «2», «4» или «8» байт;
«Два последних уровня» - результатом может быть целое число размером «4» или «8» байт.
Исправленные ошибки
Alpha.AccessPoint
В редких случаях при большом количестве сигналов в источниках Alpha.AccessPoint потреблял
большой объем памяти.
History Module
Не выполнялось чтение истории с помощью Alpha.AccessPoint, если в конфигурации модуля
был задан параметр Переопределенный идентификатор источника
Статистика
Приложение не запускалось через ярлык с использованием параметра запуска.
5.9.4
Исправленная ошибка
HDA Server
Модуль мог неверно выполнять фильтрацию событий, из-за чего в Alpha.Alarms ранее
квитированные события могли отображаться как неквитированные.
5.9.5
Исправленные ошибки
Alpha.Server, сервисные приложения
Устранена проблема, которая приводила к сбою в работе Alpha.Server и сервисных приложений
при запуске на процессорах Intel/AMD с поддержкой SHA.
SNMP Manager
В редких случаях при использовании протокола SNMPv3 модуль мог долго восстанавливать
связь с агентом.
90
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 343 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
TCP Server Module
Устранена проблема, из-за которой в редких случаях запрос Alpha.RMap мог выполняться
долгое время
5.9.7
Исправленная ошибка
OPC UA Client
Не восстанавливалось соединение с некоторыми UA серверами после их перезагрузки.
5.9.8
Улучшение
OPC UA Client
Теперь модуль получает данные узлов, которые появляются в адресном пространстве UA
сервера спустя некоторое время после его запуска, даже если UA сервер не отправляет
уведомления о создании таких узлов.
5.9.9
Исправленная ошибка
Конфигуратор
Иногда при загрузке конфигурации в формате *.xmlcfg могли возникать сбои в работе сервера.
Изменения документации
Редакция 1
Alpha.AccessPoint. Руководство администратора
Добавлено описание параметра привязки Постоянная подписка (стр. 22).
Исключена устаревшая информация по настройке хранилища модуля истории, обновлен рисунок
(стр. 35, 36).
Модуль IEC-61850 Client. Руководство администратора
Добавлено описание параметра Поддерживать соединения в резерве (стр. 23, 24).
Модуль OPC UA Client. Руководство администратора
Добавлено описание параметра адреса сигнала Триггер отправки уведомлений (стр. 16).
Добавлены примеры идентификаторов для каждого типа идентификатора (стр. 15).
Сервисное приложение Статистика. Руководство администратора
Изменено название и порт сервера лицензирования (стр. 5).
Обновлены рисунки, отображающие информацию по лицензиям (стр. 14, 15).
Модуль логики. Руководство администратора
Обновлен рисунок в примере выполнения процедуры по таймеру (стр. 11).
Модуль истории. Руководство администратора
Изменено имя файла SQL скрипта PostgreSQL(стр. 26).
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
91

=== Page 344 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Модуль Modbus TCP Master. Руководство администратора
Обновлены рисунки статистики модуля, которые отображались некорректно (стр. 30-33).
5.8
Новая возможность
Alpha.Server
Теперь запуск сервера и последующая регистрация COM-серверов может выполняться от имени
пользователя без прав администратора.
Улучшения
Modbus RTU Master, Modbus RTU Slave
Если в параметрах модулей указаны несуществующие COM-порты, то модули теперь не
запускаются.
Modbus RTU Master
При низких значениях параметра Время ожидания ответа от станции и скоростях передачи
данных в журнал работы модуля выводится рекомендуемое значение Времени ожидания ответа от
станции.
Alpha.Om
Теперь способ записи вещественных констант однозначно определяет тип значения:
1.02 - тип double;
1.02f - тип float.
ОБРАТИТЕ ВНИМАНИЕ
Нет неявного преобразования double →float, поэтому переменной типа float нельзя присвоить
значение типа double (выражения вида f : float = 42.42; компилироваться не будут).
Logics Module
Флаги обратной совместимости Режим ввода вещественных типов и Разрешить неявные
преобразования из примитивных типов в вариант для корректной компиляции процедур
предыдущей версии Alpha.Om (стр. 6).
Исправленные ошибки
Alpha.Server
Случаи сбоя в работе сервера при остановке сервера сразу после запуска.
OPC UA
Иногда модуль не предоставлял сертификат клиентам.
SNMP Manager
Сбой в работе сервера при разборе трап-уведомления с недопустимым типом данных.
При отключении сетевого интерфейса активного канала:
сервисным сигналам доступности «Available» и активности «Active» канала не
устанавливалось значение «False»;
иногда не выполнялся опрос по резервному каналу.
В журнал работы модуля записывались лишние информационные сообщения.
92
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 345 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Logics Module
Некорректный результат вычислений функции DateTime.Create при указании несуществующей
даты.
Функции обработки времени некорректно вычисляли метки времени до 1970 года.
TCP Server
Журнал приложений заполнялся сообщениями о переполнении исходящих очередей.
Modbus RTU Slave
Единичные случаи сбоя в работе сервера при перезапуске службы.
5.8.1
Исправленные ошибки
OPC UA
В составе Alpha.AccessPoint модуль требовал лицензию.
Logics Module
В конфигурации, созданной в Alpha.DevStudio, при изменении вычисляемых значений не
изменялись качество и метка времени.
5.8.2
Новая возможность
OPC UA
Опциональный переход UA сервера в состояние SUSPENDED при переходе Alpha.Server в
состояние РЕЗЕРВ.
Улучшения
Alpha.Server
Теперь резервные копии конфигурации сервера могут занимать меньше места на диске, т.к.
можно настраивать длительность их хранения (стр. 20, 31).
Исправленные ошибки
NetDiag2
В ОС Linux модуль ошибочно считал локальные сетевые карты неработоспособными, хотя
фактически сетевые карты были включены и успешно работали.
Logics Module
В конфигурации, созданной в Alpha.DevStudio, при попытках с помощью вычислений изменить
только значение сигнала изменялись качество и метка времени.
IEC-101 Master, IEC-101 Slave
Значения параметра Четность задавали неверную четность COM-порта.
5.8.3
Исправленная ошибка
HDA Server
Устранена проблема, из-за которой в Alpha.Alarms при запросе истории с фильтром не всегда
отображалось время деактивации события.
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
93

=== Page 346 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
5.8.4
Исправленная ошибка
tAlpha.AccessPoint
В редких случаях в Alpha.AccessPoint отсутствовало описание некоторых сигналов и папок.
5.8.6
Исправленные ошибки
History Module
В историю не сохранялись подавленные в Alpha.Alarms события.
В историю не сохранялись имитационные данные.
OPC UA Client
Модуль переставал принимать данные от UA-сервера, несоответствующего спецификации OPC
UA, после получения некорректных уведомлений об изменении адресного пространства. Теперь
такие уведомления игнорируются.
5.8.7
Улучшениe
IEC-61850 Client
Иногда модуль не мог получить данные с устройств, ограничивающих количество подключений к
ним, из-за того, что модуль в резерве не закрывал соединение с устройством. Теперь модуль может
закрывать соединение с устройством при переходе в резерв. Необходимость закрытия соединения
указывается в параметре Поддерживать соединения в резерве.
Исправленные ошибки
OPC DA Client
Редкие случаи сбоев в работе модуля, при которых наблюдались:
зависание приложения Статистика при просмотре статистики модуля;
неверные значение и качество сигналов;
зависание службы сервера при остановке модуля.
OPC UA Client
Вместо запроса отдельного элемента массива модуль запрашивал весь массив данных, что
иногда приводило к высокой нагрузке на сеть, Alpha.Server и опрашиваемый UA сервер.
OPC AE Server
Некоторые конфигурации, созданные в Alpha.DevStudio, ошибочно считались некорректными.
Logics Module
Повышена информативность сообщений об ошибках в конфигурации при вычислениях.
5.8.8
Исправленная ошибка
SNMP Manager
Взаимодействие с большим количеством агентов приводило к слишком высокой загрузке ЦП.
94
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 347 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
5.8.9
Улучшение
OPC UA Client
Теперь в некоторых сообщениях журнала работы модуля указываются группа серверов и код
ошибки, что упрощает диагностику проблем при взаимодействии модуля с UA сервером.
5.8.10
Улучшение
OPC UA Client
Теперь в адресе сигнала в поле Триггер отправки уведомлений можно задавать значение
параметра DataChangeTrigger подписки узла UA сервера. Возможные значения:
«STATUS_0» - уведомления генерируются если у узла изменилось только качество;
«STATUS_VALUE_1» - уведомления генерируются если у узла изменилось значение или
качество;
«STATUS_VALUE_TIMESTAMP_2» - уведомления генерируются если у узла изменилось
значение, качество или метка времени.
Примечание. Если UA сервер не поддерживает установку параметра DataChangeTrigger (в журнале
работы модуля отображается ошибка «0x80440000 - BadMonitoredItemFilterUnsupported»), то в
адресе сигнала поле Триггер отправки уведомлений следует оставить пустым. В этом случае
значение параметра DataChangeTrigger будет выставлено UA сервером по умолчанию.
Изменения документации
Редакция 2
Модуль TCP Server. Руководство администратора
Добавлено примечание о шифровании данных, передаваемых между Alpha.AccessPoint и
Alpha.Server (стр. 5).
Alpha.AccessPoint. Руководство администратора
Добавлено примечание о шифровании данных, передаваемых между Alpha.AccessPoint и
Alpha.Server (стр. 7).
Редакция 3
«Модуль OPC UA Server. Руководство администратора»
Добавлено описание параметров статистики (стр. 20).
Добавлено описание нового параметра Запретить клиентам изменение сигналов (стр. 7).
Добавлено описание нового параметра Переводить в состояние SUSPENDED при переходе
сервера в резерв (стр. 8).
Обновлено содержимое документа.
Новый документ «Модуль IEC-101 Master. Руководство администратора».
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
95

=== Page 348 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
«Модуль IEC-104 Master. Руководство администратора», «Модуль IEC-104 Slave. Руководство
администратора»
В приложении «МЭК стандартный диапазон типов» таблица идентификаторов типов разделена на
две таблицы по направлению передачи данных (стр. 31, стр. 14).
В приложении «МЭК частный диапазон типов» (стр. 34, стр. 17):
для всех идентификаторов добавлены числовые значения;
данные всех таблиц объединены в две таблицы по направлению передачи данных;
описания идентификаторов типов приведены к одному виду;
обновлены примеры адресов сигналов.
«Alpha.Server. Руководство администратора»
Добавлено описание нового атрибута «StorageDepth» конфигурации сервера, определяющего
длительность хранения резервной копии на диске (стр. 31).
Изменено представление диапазонов допустимых значений для типов float и double (стр. 34).
5.7
Новые возможности
Компонент Alpha.Imitator, предназначенный для загрузки исторических данных за указанный период
времени и проигрывания в виде потока оперативных данных (см. документ Alpha.Imitator. Руководство
администратора)
Модуль ТЭМ-104, предназначенный для сбора данных из систем теплоснабжения
OPC AE Server
Подавление и блокирование генерации событий объекта командами клиента и сервисными
сигналами
Возможность подавления и блокирования только на стороне клиента
Подавление и блокирование событий на определенное время
Ввод произвольного количества комментариев для любого события в оперативном и
историческом режимах
Модуль логики (см. документ Модуль логики. Руководство администратора)
Запуск обработчика по условию {Degree=(AnyChange)} если изменилась только метка времени
(стр. 6, )
OPC UA Client (см. документ Модуль OPC UA Client. Руководство администратора)
Настройка режима работы модуля в резерве (стр. 8)
Настройка интервала Sampling Interval для группы серверов (стр. 8)
Чтение данных типа ByteString (стр. 18)
Чтение и запись данных в элементы массива контроллера (стр. 17)
OPC DA Server
При изменении типа сигнала в сервере, возвращаемый тип данных остается неизменным до
выполнения переподписки
OPC DA Client (см. документ Модуль OPC DA Client. Руководство администратора)
Определение активного сервера резервной пары WinCC (стр. 6, 9)
OPC UA Server
Возможность подписки на атрибут DataType сигнала
96
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 349 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
Модуль резервирования (см. документ Подсистема резервирования. Руководство
администратора)
Настройка периодичности запроса состояния парного сервера (значение по умолчанию 1000 мс)
(стр. 6)
Настройка резервного перехода через состояние РАБОТА-РАБОТА (стр. 6)
Активным выбирается сервер, вес которого больше (значение сигнала
Service.Redundancy.Weight) (стр. 19)
Просмотрщик лога кадров
Поддержка загрузки внешних плагинов для просмотра журналов работы сторонних модулей
IEC104 Master (см. документ Модуль IEC-104 Master.Руководство администратора)
Настройка доверительного интервала и фильтрация входящих значений по метке времени с
учетом доверительного интервала (стр. 11, 12, 16)
Модуль истории, OPC UA Server
Поддержка двух метрок времени истории значений - сервера и источника
Modbus RTU Master, Modbus RTU Slave, Modbus TCP Master, Modbus TCP Slave, IEC101 Master,
IEC101 Slave, IEC104 Master, IEC Slave
Передача символов Кириллицы с возможностью выбора кодировки
Alpha.AccessPoint
Блокирование и подавление OPC AE источников событий
При изменении типа сигнала в сервере изменяется тип соответствующего сигнала в
Alpha.AccessPoint
Чтение истории по TCP из Alpha.Server
5.7.1
Исправленные ошибки
Alpha.AccessPoint
Не принимались настройки модуля истории от сервера более старых версий
Команды блокирования/снятия блокирования и подавления/снятия подавления отправлялись
только в активный сервер
Modbus RTU Slave
Случаи сбоя в работе сервера при перезапуске службы
При остановке сервера в журнал работы модуля записывались лишние информационные
сообщения
OPC AE Server
Ошибочно блокировались динамические события, соответствующие фильтру
Не генерировались сообщения для некоторых тегов
Logics Module
В ОС AstraLinux не выполнялась процедура обработчика из свойства 777013
OPC UA Client
Иногда модуль принимал данные с UA сервера, который не был выбран активным внутри группы
5.7.2
Исправленная ошибка
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
97

=== Page 350 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
IEC-104 Master
Редкие случаи зависания модуля
5.7.3
Исправленные ошибки
Alpha.Server, Alpha.AccessPoint
Не устанавливались совместно на одном компьютере с ОС Linux
IEC101 Master, IEC101 Slave, IEC104 Master, IEC Slave
В журналах работы модулей в поле расшифровки кадра данных некорректно отображались
значения, содержащие символы Кириллицы
HDA Server
Количество предоставляемых значений истории ограничивалось значением параметра
Максимальное количество записей в одном запросе
Просмотрщик лога кадров
В ОС Linux время в журналах работы модулей не соответствовало системному времени
Конфигуратор
При экспорте пустой конфигурации файл *.xmlcfg генерировался некорректно
5.7.4
Исправленная ошибка
OPC UA Client
При значении чувствительности сигнала AnyChange модуль не принимал изменения сигнала,
если изменилась только метка времени
5.7.5
Исправленные ошибки
OPC UA Client
Модуль получал уведомления об изменении значений узлов c неактивных серверов внутри
группы
Modbus RTU Master
В редких случаях модуль записывал входящие значения в сигналы с другими адресами
5.7.6
Новая возможность
OPC UA Server
Запрет изменения значений сигналов клиентами
5.7.7
Улучшение
98
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ

=== Page 351 ===
ИСТОРИЯ ИЗМЕНЕНИЙ
OPC UA Client
Поддержаны политики безопасности Basic256Sha256, Aes128Sha256RsaOaep,
Aes256Sha256RsaPss согласно спецификации OPC UA
5.7.8
Исправленная ошибка
HDA Server
В результат фильтрации попадали некоторые события, не соответствующие фильтру запроса
ALPHA.SERVER. ИСТОРИЯ ИЗМЕНЕНИЙ
99

=== Page 352 ===
Программный комплекс Альфа платформа
Alpha.Server 6.4
Руководство администратора
Редакция
Соответствует версии ПО
7. Предварительная
6.4.28

=== Page 353 ===
© АО «Атомик Софт», 2015-2026. Все права защищены.
Авторские права на данный документ принадлежат АО «Атомик
Софт». Копирование, перепечатка и публикация любой части или
всего документа не допускается без письменного разрешения
правообладателя.

=== Page 354 ===
Содержание
1. Об Alpha.Server
5
2. Alpha.Server в составе Альфа платформы
6
2.1. Назначение и преимущества
6
2.2. Принцип работы
7
3. Архитектура Alpha.Server
8
3.1. Архитектурная схема сервера
12
4. Подготовка к работе
13
4.1. Системные требования
13
4.2. Стандартная установка
14
4.3. Установка дополнительной копии Alpha.Server
16
4.4. Запуск и останов Alpha.Server
18
4.5. Удаление Alpha.Server
19
4.6. Ручная настройка Alpha.Server
20
5. Конфигурирование Alpha.Server
22
5.1. Принципы работы с конфигурацией
22
5.2. Принципы модульного строения
24
5.3. Настройка общих параметров модулей
24
5.4. Пример ручного создания конфигурации
27
5.5. Резервное копирование конфигурации сервера
31
5.6. Защита от несанкционированного доступа
32
5.7. Шифрование паролей
33
5.8. Контроль целостности конфигурации и БД
33
6. Сигналы Alpha.Server
34
6.1. Типы данных
34
6.2. Свойства сигналов
35
6.3. Статические и динамические сигналы
35
6.4. Возможные значения качества сигналов
36
6.5. Адресация сигналов
38
6.6. Настройка ведения детального журнала по выбранному сигналу
38
7. Сбор данных
40
8. Логическая обработка данных
41
8.1. Пересчет значений сигналов
41
8.1.1. Настройка пересчета значений сигналов
41
8.1.2. Линейный пересчет
42
8.1.3. Линейный пересчет с изломом
46
8.1.4. Инверсия битовых сигналов
48
8.2. Перекладка значений сигналов
48
8.2.1. Перекладка значения
49
8.2.2. Полная перекладка
49
8.2.3. Перекладка качества
50
8.2.4. Перекладка битов
51
8.2.5. Комбинированная перекладка
53
8.2.6. Относительная адресация при копировании
54
8.2.7. Пример перекладки
58
9. Предоставление данных
59
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
3

=== Page 355 ===
10. Приложения
60
Приложение A: Свойства сигналов Alpha.Server
60
Список терминов и сокращений
65
4
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 356 ===
1. ОБ ALPHA.SERVER
1. Об Alpha.Server
Alpha.Server – это программный комплекс для обмена данными между технологическим оборудованием и
компонентами проекта. С его помощью можно:
собирать данные о состоянии технологического процесса;
предоставлять собранные данные персоналу;
доставлять команды персонала оборудованию.
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
5

=== Page 357 ===
2. ALPHA.SERVER В СОСТАВЕ АЛЬФА ПЛАТФОРМЫ
2. Alpha.Server в составе Альфа платформы
С помощью Alpha.Server компоненты Альфа платформы взаимодействуют друг с другом и с
технологическим оборудованием. Например, получив данные от ПЛК, Alpha.Server отправляет их в
Alpha.HMI для предоставления персоналу и в Alpha.Historian для архивации.
2.1. Назначение и преимущества
Основной задачей Alpha.Server, как компонента Альфа платформы, является выполнение функций сбора,
обработки и предоставления данных. Alpha.Server выполняет сбор технологических данных с
коммуникационных устройств в ходе мониторинга контролируемых объектов. На основе полученной
информации осуществляется контроль над технологическим процессом. Управление может происходить как
по команде оператора, при передаче собранных данных на верхние уровни АСУ ТП, так и по встроенным
алгоритмам.
Alpha.Server является шлюзом для работы SCADA-системы с устройствами ввода/вывода информации.
Одновременно сервер может поддерживать соединение с несколькими промышленными контроллерами.
Установка нескольких экземпляров Alpha.Server на одном компьютере решает задачу конвертации
протоколов (например, Modbus в ГОСТ Р МЭК или в OPC).
Alpha.Server используется как часть автоматизированной системы управления, построенной на базе Альфа
платформы. В основе АСУ данного уровня лежит максимальная интеграция компонентов системы,
вследствие этого согласованность в обработке данных и выполнении команд. Компонент Alpha.Server,
благодаря данному принципу, характеризуется высокой производительностью при обмене данных с
объектами управления, расположенными на верхних уровнях системы управления. В процессе
проектирования Альфа платформы была учтена угроза потери данных в случае сбоев в работе. В
результате при внедрении АСУ в среде исполнения применяется резервирование сервера и каналов связи.
Посредством резервирования обеспечивается также высокий уровень надёжности и гарантируется
своевременная и бесперебойная доставка событий и команд.
Alpha.Server может использоваться как в локальных системах управления, так и в распределённых
промышленных предприятиях. Alpha.Server, входящие в состав АСУ, работающих на различных объектах
единого предприятия, поддерживают соединение друг с другом на сетевом уровне.
6
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 358 ===
2. ALPHA.SERVER В СОСТАВЕ АЛЬФА ПЛАТФОРМЫ
2.2. Принцип работы
Полноценное функционирование Alpha.Server не ограничено временными границами. Сервер может
стабильно работать в режиме 24/7 (двадцать четыре часа, семь дней в неделю) с сохранением всех
возможностей. Перезапуск сервера требуется только для выполнения конфигурационных настроек (стр. 22).
Alpha.Server характеризуется высокой производительностью, о чём свидетельствует возможность ядра
выполнять более 2 000 000 операций в секунду. Корректная работа сервера не нарушается при обработке
значений более 1 000 000 сигналов и выполнении ядром более 1 000 000 операций уведомления.
Управляющие команды, получаемые сервером, с учётом выделенного им места в очереди отправляющим
объектом, оперативно передаются на уровень ниже. При передаче команд управления гарантируется высокая
скорость передачи и сохранность передаваемых данных.
Работа с Alpha.Server организована в двух режимах: основной и резервный. Благодаря резервированию
серверов повышается их надёжность и обеспечивается сохранность собранных технологических данных в
случае сбоев в работе. Включение в работу резервного сервера производится диспетчером вручную, либо
автоматически в случае отсутствия связи с одним из серверов. Работая в режиме резерва, сервер задаёт
условия работы коммуникационных модулей, входящих в его состав. Модули, находящиеся в резервном
режиме, не отправляют управляющих воздействий. В результате, механизм резервирования также снижает
нагрузку на оборудование, что увеличивает скорость выполнения операций.
Основными составляющими Alpha.Server являются программные модули. Один экземпляр Alpha.Server
содержит до 64 модулей. Набор модулей не является постоянным и подбирается в соответствии с задачами
проекта автоматизации (стр. 24).
В комплект поставки Alpha.Server входят также сервисные приложения для управления, конфигурирования,
просмотра статистической информации. Данные приложения предназначены для установки на
автоматизированных рабочих местах администраторов. Все сообщения о работе сервера и его компонентов
фиксируются в журнал приложений ОС.
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
7

=== Page 359 ===
3. АРХИТЕКТУРА ALPHA.SERVER
3. Архитектура Alpha.Server
Alpha.Server – компонент Альфа платформы, выполняющий следующие задачи:
сбор данных с устройств в ходе мониторинга контролируемых объектов;
предоставление данных клиентам по различным протоколам и спецификациям;
повышение надежности проекта за счёт резервирования;
логическая обработка данных в режиме реального времени;
генерация событий и тревог на основе полученных данных.
Сервер построен по модульному принципу, что позволяет конфигурировать его в зависимости от
выполняемых задач и не создавать лишней нагрузки.
Количество экземпляров сервера на одном компьютере не ограничено, что позволяет использовать сервер в
качестве конвертера протоколов или для создания демилитаризованных зон.
Сбор данных
Alpha.Server обеспечивает опрос источников данных по различным протоколам и спецификациям.
Протокол/спецификация
Модуль сервера
Поддержка в ОС
Windows
Linux
ГОСТ Р МЭК 60870-5-101
IEC-101 Master
ü
ü
ГОСТ Р МЭК 60870-5-104
IEC-104 Master
ü
ü
ГОСТ Р МЭК 61850
IEC-61850 Client
ü
ü
Modbus TCP
Modbus TCP Master
ü
ü
Modbus RTU
Modbus RTU Master
ü
ü
OPC DA
OPC DA Client
ü
OPC HDA
OPC HDA Client
ü
OPC UA
OPC UA Client
ü
ü
SQL
SQL Connector
ü
ü
SNMP
SNMP Manager
ü
ü
Syslog
Syslog Server
ü
ü
BACnet
BACnet Client
ü
ü
FINS
FINS Client
ü
ü
NFL
NFL Client
ü
ü
S7
Siemens S7 Client
ü
ü
8
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 360 ===
3. АРХИТЕКТУРА ALPHA.SERVER
Протокол/спецификация
Модуль сервера
Поддержка в ОС
Windows
Linux
UNET
UNET Client
ü
ü
EtherNet/IP
EtherNet/IP Scanner
ü
ü
Предоставление данных клиентам
Alpha.Server предоставляет данные клиентам по различным протоколам и спецификациям.
Протокол/спецификация
Модуль сервера
Поддержка в ОС
Windows
Linux
ГОСТ Р МЭК 60870-5-101
IEC-101 Slave
ü
ü
ГОСТ Р МЭК 60870-5-104
IEC-104 Slave
ü
ü
Modbus TCP
Modbus TCP Slave
ü
ü
Modbus RTU
Modbus RTU Slave
ü
ü
OPC DA
OPC DA Server
ü
OPC HDA
HDA Server
ü
OPC AE
OPC AE Server
ü
OPC UA
OPC UA Server
ü
ü
TCP
TCP Server
ü
ü
Файловый интерфейс
TCP Server
ü
ü
Ядро
Ядро Alpha.Server является центральным компонентом сервера. Предназначено для реализации
инфраструктуры сервера, интерфейсов работы с модулями, сигналами и их свойствами, остальными
подсистемами. Ядро может производить значимые логические вычисления, требующие наибольшей
скорости вычислений. Такой подход позволяет значительно повысить производительность работы сервера.
Все вычисления производятся по описанным при конфигурировании алгоритмам.
Основные функции ядра Alpha.Server:
пересчет значений из физических значений в инженерные и в обратном направлении. При пересчете
используются линейная и линейная с изломом зависимости;
выполнение алгоритмов по событию, таймеру и расписаниям;
управление запуском и остановом модулей при старте и в процессе работы сервера;
управление состоянием сервера в рамках резервирования;
запись и чтение данных из ОБД;
управление модулями, отправка и принятие уведомлений об изменении значений сигналов.
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
9

=== Page 361 ===
3. АРХИТЕКТУРА ALPHA.SERVER
Резервирование
Модуль сервера
Поддержка в ОС
Windows
Linux
Модуль резервирования
ü
ü
Alpha.Server реализует два вида резервирования:
горячее резервирование;
полное дублирование.
При горячем резервировании система позволяет настроить репликацию данных между резервируемыми
серверами для поддержания оперативной базы данных резервного сервера в актуальном состоянии. Тонкая
настройка сервера позволяет ограничивать функции сервера в состоянии резерва в широком диапазоне
(полное или частичное отключение опроса и обработки данных).
При полном дублировании, серверы работают независимо друг от друга и оба доступны для работы с
клиентами. В этом случае клиентское приложение само решает с каким сервером работать. При реализации
крупных распределенных проектов с организацией резервируемых пунктов управления возможно создание
единой системы резервных пар серверов.
Логическая обработка данных
Модуль сервера
Поддержка в ОС
Windows
Linux
Logics Module
ü
ü
Data Buffer
ü
ü
Write VQT
ü
ü
Одна из первостепенных задач Alpha.Server – промежуточная обработка данных. Для повышения
производительности работы Alpha.Server все вычисления, производимые при обработке параметров,
вынесены на уровень ядра. За внутресерверные вычисления отвечает Logics Module. Алгоритмы модуля
логики составляются на специальном скриптовом языке Alpha.Om.
Возможности логической обработки данных:
пересчет значений из физических в инженерные и обратно (по линейной и линейной с изломом
зависимостям);
пересчет значений сигналов по формуле;
выполнение алгоритмов по событию, таймеру или расписанию;
вызов функций из внешних динамических библиотек;
перехват генерируемых событий и тревог.
Специфичные задачи логической обработки:
разбор буфера для выделения кода технологического объекта и кода события (тревоги) (модуль
Data Buffer);
опциональное изменение свойств сигнала Value, Quality или Timestamp (модуль Write VQT).
10
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 362 ===
3. АРХИТЕКТУРА ALPHA.SERVER
Генерация событий и тревог
Модуль сервера
Поддержка в ОС
Windows
Linux
OPC AE Server
ü
ü
Модуль рассылки событий
ü
ü
ОБРАТИТЕ ВНИМАНИЕ
В ОС Linux модуль OPC AE Server генерирует события, но не предоставляет их.
На основе полученных и обработанных данных, сервер может по заранее определенным правилам и
алгоритмам генерировать и предоставлять пользователям сообщения о событиях и тревогах. Сервер
генерирует события по нескольким алгоритмам срабатывания: дискретный переключатель, перечисление,
отклонение, по уровню (модуль OPC AE Server).
Возможности сервера по генерации событий и тревог:
генерация событий в рамках спецификации OPC AE;
предоставление информации о событиях в рамках спецификации OPC DA (только в ОС Windows);
отправка информации о событиях по электронной почте (Модуль рассылки событий).
Прочие возможности Alpha.Server
Модуль сервера
Поддержка в ОС
Windows
Linux
SnapShot
ü
ü
FS Generator
ü
NetDiag
ü
NetDiag2
ü
ü
Модуль истории
ü
ü
ProcessMonitor
ü
ü
Прочие возможности Alpha.Server:
сохранение текущих значений сигналов в файл-срезы XML-формата (модуль SnapShot);
сохранение текущих значений сигналов в файл-срезы бинарного формата (модуль FS Generator);
диагностика сетевых устройств (модули NetDiag, NetDiag2);
предоставление данных для записи в сервер истории (Модуль истории).
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
11

=== Page 363 ===
3. АРХИТЕКТУРА ALPHA.SERVER
Сервисное обслуживание Alpha.Server
Обслуживание сервера выполняется сервисными приложениями, которые входят в состав клиентской части
дистрибутива Alpha.Server (только в ОС Windows):
Редактирование конфигурации сервера выполняется с помощью сервисного приложения
Конфигуратор.
Просмотр статистической информации о работе сервера выполняется с помощью сервисного
приложения Статистика.
Просмотр журналов работы модулей сервера выполняется с помощью сервисного приложения
Просмотрщик лога кадров.
Комплексное обслуживание, администрирование и управление сервером или резервной парой
серверов выполняется с помощью сервисного приложения Управляющий.
Также для сервисных и диагностических целей при работе с проектами автоматизации применяется
набор инструментов Alpha.Tools.
3.1. Архитектурная схема сервера
12
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 364 ===
4. ПОДГОТОВКА К РАБОТЕ
4. Подготовка к работе
4.1. Системные требования
Alpha.Server функционирует в виде:
службы Alpha.Server в ОС Windows;
сервиса alpha.server.service в ОС Linux.
На одном компьютере одновременно могут работать несколько экземпляров Alpha.Server (стр. 16).
Количество серверов на одном компьютере ограничено его производительностью. Совместная нагрузка
процессора при наличии нескольких экземпляров сервера не должна превышать 70%. Работа Alpha.Server
возможна без открытия сеанса пользователя.
ОБРАТИТЕ ВНИМАНИЕ
Для корректной работы проекта автоматизации большой информационной ёмкости с большим
количеством источников данных важна не только частота работы процессора, но и количество
ядер/потоков.
За рекомендациями по системным требованием компьютера для установки серверной части
Alpha.Server для конкретного проекта автоматизации обратитесь в техническую поддержку АО
«Атомик Софт» по электронной почте support@automiq.ru или офис продаж по электронной почте
sales@automiq.ru.
Ниже приведены системные требования компьютера для установки серверной части Alpha.Server с целью
ознакомления с его функциями, запуска и работы проекта автоматизации верхнего уровня небольшой
информационной ёмкости:
ОС
Microsoft Windows 10 Pro/11 Pro
Microsoft Windows Server 2012/2012 R2/2016/2019/2022
Astra Linux, РЕД ОС, Ubuntu, ОС семейства "Альт" (glibc не ниже 2.17)
Разрядность
ОС
x64
Процессор
Intel Celeron с тактовой частотой не менее 1.6 ГГц
Объем
оперативной
памяти
не менее 2 ГБ
Объем
дисковой
памяти
не менее 1 ГБ
Сетевой
адаптер
Ethernet 10/100/1000 Мбит/с
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
13

=== Page 365 ===
4. ПОДГОТОВКА К РАБОТЕ
Установленное
ПО
Для OC Windows:
Антивирусное ПО
OPC Core Components версии 105.1 (ссылка для скачивания:
https://opcfoundation.org/developer-tools/samples-and-tools-classic/core-components)
Системные требования компьютера для установки клиентской части Alpha.Server:
ОС
Microsoft Windows 10 Pro/11 Pro
Microsoft Windows Server 2012/2012 R2/2016/2019/2022
Разрядность
ОС
x64
Процессор
Intel Celeron с тактовой частотой не менее 1.6 ГГц
Объем
оперативной
памяти
не менее 1 ГБ
Объем
дисковой
памяти
не менее 500 МБ
Сетевой
адаптер
Ethernet 10/100/1000 Мбит/с
Установленное
ПО
Антивирусное ПО
.NET 4.6.1 (ссылка для скачивания: https://www.microsoft.com/ru-
ru/download/details.aspx?id=49982)
OPC .NET API 2.00 Redistributables 105.0 (ссылка для скачивания:
https://opcfoundation.org/developer-tools/samples-and-tools-classic/net-api-sample-client-
source-code)
4.2. Стандартная установка
ОС Windows
ОБРАТИТЕ ВНИМАНИЕ
Для установки Alpha.Server следует выполнить вход в систему с правами администратора ОС.
Для установки Alpha.Server:
1. Запустите дистрибутив Alpha.Server-х.x.x+xx.xxxxx (x64).msi.
2. По умолчанию устанавливаются все компоненты Alpha.Server:
14
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 366 ===
4. ПОДГОТОВКА К РАБОТЕ
серверная часть;
клиентская часть, состоящая из сервисных приложений:
Управляющий;
Конфигуратор;
Просмотрщик лога кадров;
Статистика.
Если необходимо установить только один из компонентов, в параметрах установки заблокируйте
компонент, который устанавливать не нужно:
3. Следуйте указаниям мастера установки.
Каталоги установки компонентов Alpha.Server по умолчанию:
серверная часть – C:\Program Files\Automiq\Alpha.Server\Server;
клиентская часть – C:\Program Files\Automiq\Alpha.Server\Service.
ОС Linux
В ОС Linux устанавливается только серверная часть Alpha.Server. Установка выполняется штатным
пакетным менеджером.
ОБРАТИТЕ ВНИМАНИЕ
Команда установки выполняется только от суперпользователя «root».
Имя устанавливаемого пакета: alpha.server-x.x.x+xx.xxxxx.deb или alpha.server-x.x.x+xx.xxxxx.rpm в
зависимости от используемой ОС Linux. Находясь в папке с установочным пакетом, запустите установку.
Установка пакета *.rpm с помощью пакетного менеджера YUM:
yum install alpha.server-x.x.x+xx.xxxxx.rpm
Установка пакета *.rpm с помощью пакетного менеджера RPM:
rpm -i alpha.server-x.x.x+xx.xxxxx.rpm
Установка пакета *.deb с помощью пакетного менеджера apt:
apt-get install alpha.server-x.x.x+xx.xxxxx.deb
Установка пакета *.deb с помощью пакетного менеджера dpkg:
sudo dpkg -i alpha.server-x.x.x+xx.xxxxx.deb
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
15

=== Page 367 ===
4. ПОДГОТОВКА К РАБОТЕ
Alpha.Server устанавливается в директорию /opt/Automiq/Alpha.Server.
4.3. Установка дополнительной копии Alpha.Server
OC Windows
Чтобы установить два экземпляра Alpha.Server на одном компьютере под управлением ОС Windows:
1. Установите Alpha.Server стандартным способом. По умолчанию Alpha.Server устанавливается в
папку C:\Program Files\Automiq\Alpha.Server.
2. Скопируйте папку C:\Program Files\Automiq\Alpha.Server со всем содержимым в новую папку,
например, с именем C:\Program Files\Automiq\Alpha.Server1.
3. Откройте настроечный xml-файл копии Alpha.Server: C:\Program
Files\Automiq\Alpha.Server1\Server\Alpha.Server.xml.
4. Внесите следующие изменения в настроечный файл:
Измените значение атрибута ServiceName (атрибут элемента install) – имя службы сервера.
Например:
ServiceName = "Alpha.Server1"
Измените значения идентификатора ProgID и класса CLSID для каждого регистрируемого COM-
сервера. Например, для COM-сервера OPCDA:
ProgID="AP.OPCDAServer.1" CLSID="{ED738D76-9CDF-4C05-92EB-5268345B6F4F}";
для COM-сервера OPCAE:
ProgID="AP.OPCAEServer.1" CLSID="{A439CED6-0D7F-43A5-BD97-BEA80507C04A}"
для COM-сервера HDA:
ProgID="AP.HDAServer.1" CLSID="{95774D45-B3FF-4B82-9B44-09B07DAF9C58}"
Измените значение атрибута Port (атрибут элемента Connection) – номер порта подключения к
серверу. Например:
Connection Port="4573"
Измените значение атрибута ID (атрибут элемента Instance) - идентификатор экземпляра.
Например:
Instance ID="589745A2-5A75-4C4E-8540-B3795A0B2EF2
Вид файла Alpha.Server.xml копии сервера с измененными атрибутами имеет вид:
<?xml version="1.0" encoding="windows-1251"?>
<configuration>
<install ServiceName="Alpha.Server1" ExeName="Alpha.Server.exe">
<ComServers>
<OPCDA ProgID="AP.OPCDAServer.1" CLSID="{28A2AD9C-C45E-4C6b-A0C3-
6E363F99CA72}" />
16
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 368 ===
4. ПОДГОТОВКА К РАБОТЕ
<OPCAE ProgID="AP.OPCAEServer.1" CLSID="{0CAEA48A-D7E6-44A4-85FD-
C27836727D07}" />
<HDA ProgID="AP.HDAServer.1" CLSID="{8002740A-886F-1488-2280-
42058D6D5CA8}" />
</ComServers>
</install>
<Storage Filename="AlphaServer.cfg" />
<Connection Port="4573" />
<Backup Path="..\Backups" Time="00:00" StorageDepth="14" />
<Log Path="..\Logs" />
<Dispatch Model="Default" />
<Config ReadOnly="False" />
<Instance ID="589745A2-5A75-4C4E-8540-B3795A0B2EF2" />
<Culture LangID="ru-RU" />
</configuration>
5. Зарегистрируйте копию Alpha.Server. Для этого в командной строке, находясь в папке C:\Program
Files\Automiq\Alpha.Server1\Server, выполните команду:
Alpha.ServerInstaller.exe /install
6. Запустите копию Alpha.Server.
7. Подключитесь тестовым клиентом и убедитесь в доступности модулей и сигналов Alpha.Server.
OC Linux
Чтобы добавить дополнительный экземпляр сервиса Alpha.Server на одном компьютере под управлением
ОС Linux:
1. Скопируйте существующую папку Alpha.Server командой:
cp -R /opt/Automiq/Alpha.Server /opt/Automiq/Alpha.Server2
2. Перейдите в добавленную папку и измените в файле Alpha.Server.xml:
имя сервиса в атрибуте ServiceName (атрибут элемента install):
ServiceName = "Alpha.Server2"
номер порта подключения к Alpha.Server в атрибуте Port (атрибут элемента Connection):
Connection Port="4573"
идентификатор экземпляра в атрибуте ID (атрибут элемента Instance):
Instance ID="589745A2-5A75-4C4E-8540-B3795A0B2EF2
3. Скопируйте unit-файл сервиса Alpha.Server командой:
sudo cp /lib/systemd/system/alpha.server.service
/lib/systemd/system/alpha.server2.service
4. Откройте добавленный файл командой:
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
17

=== Page 369 ===
4. ПОДГОТОВКА К РАБОТЕ
sudo nano /lib/systemd/system/alpha.server2.service
В открывшемся файле измените:
описание сервиса в параметре Description (раздел Unit):
Description=Alpha.Server2
путь к папке Alpha.Server в параметре WorkingDirectory (раздел Service):
WorkingDirectory=/opt/Automiq/Alpha.Server2
путь к библиотекам Alpha.Server в параметре LD_LIBRARY_PATH (раздел Service):
Environment=LD_LIBRARY_PATH=/opt/Automiq/Alpha.Server2
путь к исполняемому файлу в параметре ExecStart (раздел Service):
ExecStart=/opt/Automiq/Alpha.Server2/Alpha.Server
5. Зарегистрируйте и запустите новый экземпляр сервиса Alpha.Server командами:
sudo systemctl enable alpha.server2
sudo systemctl start alpha.server2
4.4. Запуск и останов Alpha.Server
ОС Windows
Управление сервером выполняется путем запуска/перезапуска/останова службы Alpha.Server
стандартными инструментами ОС Windows.
Управление сервером в составе резервной пары возможно через сервисное приложение Управляющий.
ОС Linux
Управление сервером выполняется путем запуска/перезапуска/останова сервиса alpha.server
специализированными командами.
ОБРАТИТЕ ВНИМАНИЕ
Все команды выполняются только от суперпользователя «root».
Запуск:
systemctl start alpha.server
Останов:
18
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 370 ===
4. ПОДГОТОВКА К РАБОТЕ
systemctl stop alpha.server
Перезапуск:
systemctl restart alpha.server
4.5. Удаление Alpha.Server
ОС Windows
Удаление Alpha.Server и вспомогательного ПО выполняется стандартными инструментами:
1. Запустите Программы и компоненты: Пуск →Панель управления →Программы и компоненты.
2. Из представленного списка установленных программ выберите Alpha.Server и нажмите кнопку
Удалить.
При удалении Alpha.Server выполняется удаление всех установленных серверных и сервисных компонентов
Alpha.Server. Возможно выборочное удаление компонентов путём блокирования одной из частей в процессе
удаления.
Чтобы удалить дополнительную копию Alpha.Server:
1. Разрегистрируйте копию Alpha.Server. Для этого в командной строке, находясь в папке C:\Program
Files\Automiq\Alpha.Server1\Server, выполните команду:
Alpha.ServerInstaller.exe /uninstall
2. Вручную удалите папку C:\Program Files\Automiq\Alpha.Server1 со всеми файлами.
ОС Linux
Удаление Alpha.Server выполняется штатным пакетным менеджером.
ОБРАТИТЕ ВНИМАНИЕ
Команда удаления выполняется только от суперпользователя «root».
Удаление пакета *.rpm с помощью пакетного менеджера YUM:
yum remove alpha.server
Удаление пакета *.rpm с помощью пакетного менеджера RPM:
rpm -e alpha.server
Удаление пакета *.deb с помощью пакетного менеджера apt:
apt-get remove alpha.server
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
19

=== Page 371 ===
4. ПОДГОТОВКА К РАБОТЕ
Удаление пакета *.deb с помощью пакетного менеджера dpkg:
dpkg -r alpha.server
4.6. Ручная настройка Alpha.Server
Ручная настройка может потребоваться после установки Alpha.Server для изменения стандартных
параметров:
расположение и имя бинарного файла конфигурации сервера;
номер порта подключения к серверу;
время выполнения автоматического резервного копирования;
папка хранения резервных копий конфигурации сервера;
папка хранения журналов работы модулей.
Параметры настройки сервера задаются в файле Alpha.Server.xml, расположенном:
в ОС Windows в папке C:\Program Files\Automiq\Alpha.Server\Server;
в ОС Linux в директории /opt/Automiq/Alpha.Server.
Файл по умолчанию имеет следующий вид:
<?xml version="1.0" encoding="windows-1251"?>
<configuration>
<install ServiceName="Alpha.Server" ExeName="Alpha.Server.exe">
<ComServers>
<OPCDA ProgID="AP.OPCDAServer" CLSID="{28A2AD9C-C45E-4C6b-A0C3-
6E363F99CA72}" />
<OPCAE ProgID="AP.OPCAEServer" CLSID="{0CAEA48A-D7E6-44A4-85FD-
C27836727D07}" />
<HDA ProgID="AP.HDAServer" CLSID="{8002740A-886F-1488-2280-42058D6D5CA8}"
/>
</ComServers>
</install>
<Storage Filename="AlphaServer.cfg" />
<Connection Port="4572" />
<Backup Path="..\Backups" Time="00:00" StorageDepth="14" />
<Log Path="..\Logs" />
<Dispatch Model="Default" />
<Config ReadOnly="False" />
<Instance ID="589745A2-5A75-4C4E-8540-B3795A0B2EF1" />
<Culture LangID="ru-RU" />
<MasterPassword
Cipher="icj+2PDqNPRFKuxi6q+XmyvU9QSEyS3iDtChbTKBIBWiuqo0Yslg7wOJz47D5UB02xeBurGx
CB0bPbZi8KSeX09CAZAIw8lyRYkPlCNhWA+NNq5X+ADZScDJmMEfDErpClJxCing7+2t3PiCjJWoxZAw
KpLWu1hmw9/QdikYQ9E" />
</configuration>
Допустимо изменение значений следующих атрибутов:
20
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 372 ===
4. ПОДГОТОВКА К РАБОТЕ
Родительский
элемент
Атрибут
Описание
Storage
Filename
Полный путь или название файла конфигурации сервера
Connection
Port
Номер порта подключения к серверу
Backup
Path
Папка хранения автоматически создаваемых резервных копий
конфигурации. Резервные копии по умолчанию сохраняются в папку
C:\Program Files\Automiq\Alpha.Server\Backups с именами в
формате:
[Год]_[Месяц]_[Дата] [номер копии] [имя
пользователь].backup;
Backup
Time
Время автоматического создания резервной копии текущей
конфигурации
Backup
StorageDepth
Длительность хранения резервных копий конфигурации сервера,
указывается в сутках. Диапазон допустимых значений от 0 до 90
Log
Path
Папка хранения журналов работы модулей сервера
Dispatch
Model
Модель исполнения Alpha.Server:
«Default» - модель исполнения по умолчанию;
«Transactional» - транзакционная модель исполнения.
Config
ReadOnly
Возможность редактирования конфигурации Alpha.Server через
сервисное приложение Конфигуратор:
«False» - редактирование конфигурации разрешено;
«True» - редактирование запрещено, возможны только
открытие и просмотр конфигурации. Возможность редактирования
конфигурации через Alpha.DevStudio при этом сохраняется.
Instance
ID
Идентификатор экземпляра Alpha.Server. Каждый экземпляр
Alpha.Server на одном компьютере или в резервной паре должен иметь
свой уникальный идентификатор.
MasterPassword
Cipher
Запись о пароле доступа к экземпляру сервера в зашифрованном виде,
если пароль был задан в сервисном приложении Конфигуратор.
После внесения изменений в файл Alpha.Server.xml сохраните и перезапустите службу Alpha.Server в ОС
Windows или сервис alpha.server в Linux системах.
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
21

=== Page 373 ===
5. КОНФИГУРИРОВАНИЕ ALPHA.SERVER
5. Конфигурирование Alpha.Server
Alpha.Server, как компонент Альфа платформы, может быть сконфигурирован следующими способами:
как отдельный компонент через сервисное приложение Конфигуратор;
в составе проекта автоматизации с использованием Alpha.DevStudio, при этом конфигурация
Alpha.Server компилируется из общей конфигурации проекта.
5.1. Принципы работы с конфигурацией
Конфигурация Alpha.Server хранится в бинарном файле AlphaServer.cfg. Файл расположен в
папке/директории установки Alpha.Server.
Конфигурация Alpha.Server характеризуется:
номером версии конфигурации;
идентификатором конфигурации.
Номер версии конфигурации увеличивается при любых изменениях конфигурации сервера. Текущий номер
версии конфигурации можно узнать через:
сервисное приложение Статистика;
сигнал с тегом «Service.Config.Version», значение которого можно просмотреть любым OPC
клиентом.
Конфигурация сервера имеет уникальный идентификатор, который содержится в сигнале с тегом
«Service.Id.Str». Идентификатор конфигурации также представлен в виде 16-байтового числа. Младшие 8
байт идентификатора содержатся в сигнале с тегом «Service.Id.Low», старшие - в сигнале с тегом
«Service.Id.High». Данные сигналы можно смотреть любым OPC клиентом.
Также идентификатор можно узнать, открыв экспортированный файл конфигурации в текстовом редакторе.
22
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 374 ===
5. КОНФИГУРИРОВАНИЕ ALPHA.SERVER
<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!--файл конфигурации. Время создания: 9:00:27 05.07.2023, пользователь -
Administrator, компьютер - TESTER -->
<Configuration Id="e98e62c1-3a74-468d-a9d5-220bac075270" Format="1">
Конфигурация Alpha.Server содержит:
структура дерева сигналов - полный список сигналов, которые добавлены в конфигурацию;
инициализирующие значения сигналов - значения, которые сигналы принимают при запуске сервера;
модульный состав сервера - полный список модулей, которые добавлены в конфигурацию;
конфигурационные параметры модулей и их значения;
пароль доступа к серверу.
При старте сервера выполняется следующий порядок операций:
1. Конфигурация считывается из файла AlphaServer.cfg.
2. Сигналам присваиваются инициализирующие значения.
3. Модули запускаются в нужной последовательности и согласно конфигурационным параметрам.
4. Модули достраивают дерево сигналов динамическими сигналами (стр. 35).
К адресному пространству сервера для работы с сигналами могут подключиться несколько OPC клиентов
одновременно.
ОБРАТИТЕ ВНИМАНИЕ
Все изменения значений сигналов и свойств сигналов, которые произведены с помощью OPC
клиента, не записываются в файл AlphaServer.cfg. После перезапуска Alpha.Server сигналы
примут свои исходные инициализирующие значения.
Редактировать конфигурацию Alpha.Server можно только с помощью сервисного приложения
Конфигуратор. Изменения могут касаться состава дерева сигналов, списка модулей сервера,
инициализирующих значений сигналов.
С конфигурацией можно работать в многопользовательском режиме. Для избежания конфликтов при
совместной работе в Конфигураторе реализован механизм блокировки узлов и веток дерева сигналов или
модулей. При редактировании любого узла конфигурации данный узел нужно блокировать для остальных
пользователей. Также можно заблокировать целую ветку узлов. Далее работать с заблокированным узлом
или веткой может только заблокировавший пользователь до снятия блокировки.
Блокировка веток и узлов конфигурации производится с помощью инструмента
на панели инструментов
или командами главного меню Блокировки →Заблокировать ветку/Заблокировать узел. Снимается
блокировка с помощью инструмента
на панели инструментов или командой главного меню Блокировки →
Снять блокировку.
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
23

=== Page 375 ===
5. КОНФИГУРИРОВАНИЕ ALPHA.SERVER
ПРИМЕЧАНИЕ
В OPC клиентах измененная конфигурация сервера будет доступна только после перезапуска
Alpha.Server.
Чтобы защитить конфигурацию сервера от потери данных, создавайте резервные копии текущей
конфигурации (стр. 31). Сохраненные конфигурационные файлы могут быть обратно импортированы.
Экспортировать и импортировать конфигурацию сервера в формате *.xmlcfg и *.csv можно с помощью
сервисного приложения Конфигуратор.
Чтобы экспортировать конфигурацию, в пункте меню Файл выберите Сохранить конфигурацию в файл....
Чтобы импортировать конфигурацию из файла, в пункте меню Файл выберите Загрузить конфигурацию из
файла....
Файлы конфигурации формата *.xmlcfg доступны для просмотра с помощью текстового редактора. Файлы
формата *.csv открываются с помощью MS Excel и имеют вид структурированной таблицы.
ОБРАТИТЕ ВНИМАНИЕ
После всех изменений конфигурации или после импорта конфигурации необходимо перезапустить
Alpha.Server.
5.2. Принципы модульного строения
Многие возможности Alpha.Server реализуются модулями - специальными библиотеками. Так, весь обмен
данными по стандартным протоколам - МЭК 870-5, MODBUS, SNMP и другим - реализуется как раз с
использованием модулей.
Одни модули могут получать данные и сохранять их как значения сигналов, другие модули могут
предоставлять потребителям хранящиеся в сигналах данные. Например, модуль Modbus TCP Master
запрашивает у станции Modbus значение какого-нибудь технологического параметра и сохраняет его в виде
значения некоторого сигнала.
Один и тот же сигнал может одновременно использоваться разными модулями. Например, модуль Modbus
TCP Master может записать значение параметра в сигнал, а затем модуль OPC UA Server передаст
значение этого сигнала в Alpha.HMI.
5.3. Настройка общих параметров модулей
После формирования списка модулей настройте параметры их работы. Все модули обладают общим и
уникальным наборами параметров. Уникальные параметры узла конфигурации модуля содержатся в группе
Дополнительные и настраиваются для каждого модуля индивидуально.
24
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 376 ===
5. КОНФИГУРИРОВАНИЕ ALPHA.SERVER
Общие параметры узла конфигурации модуля содержатся в группе Общие:
Параметр
Описание
Имя модуля
Название модуля
Идентификатор
модуля
Идентификатор модуля в Alpha.Server
Активность
Активность модуля:
«Да» – модуль запущен
«Нет» – модуль остановлен
Уровень
трассировки в
журнал
приложений
Типы сообщений, которые фиксируются в журнал приложений:
«Предупреждения и аварийные сообщения» – логические ошибки, ошибки работы
модуля Alpha.Server. Предупреждения содержат некритичные ошибки. Аварийные
сообщения информируют об ошибках, которые влияют на работоспособность
Alpha.Server;
«Информационные сообщения» – сообщения, которые показывают основную
информацию о работе модуля;
«Отладочные сообщения» – сообщения, которые наиболее детально отражают
информацию о работе модуля.
Вышестоящий уровень входит в состав нижестоящего. Если установлен уровень
«Информационные сообщения», то в журнал фиксируются «Предупреждения и аварийные
сообщения» и «Информационные сообщения»
Вести журнал
работы модуля
Параметр, показывающий ведется ли запись сообщений о работе модуля в журнал
работы модуля:
«Да» – сведения о работе модуля сохраняются в журнал
«Нет» – журнал работы модуля не ведётся
Размер журнала
работы модуля,
МБ
Размер файла журнала работы модуля в мегабайтах. При достижении максимального
размера создается новый файл, копия старого файла хранится на рабочем диске
Количество
дополнительных
журналов
работы
Количество файлов заполненных журналов работы модуля. Минимальное значение
параметра равно «1». Максимальное количество файлов журнала равно «255».
Значения общих параметров таких как Активность («Active»), Вести журнал работы модуля
(«FrameLogEnable»), Идентификатор модуля («Id») и Уровень трассировки в журнал приложений
(«SystemLogTraceLevel»), вы можете посмотреть в любом OPC DA клиенте по тегу:
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
25

=== Page 377 ===
5. КОНФИГУРИРОВАНИЕ ALPHA.SERVER
Service.Modules.Имя модуля.Имя параметра
Ведение журнала работы для каждого модуля настраивается при конфигурировании модуля. Для каждого
модуля создается отдельный файл:
в ОС Windows в папке C:\Program Files\Automiq\Alpha.Server\Logs;
в ОС Linux в директории /opt/Automiq/Alpha.Server/Logs.
Ведение журнала работы для каждого модуля настраивается при конфигурировании модуля. Для каждого
модуля создается отдельный файл. Расположение файлов журналов работы указывается в файле
Alpha.Server.xml в атрибуте Path элемента Log (по умолчанию Logs в папке/директории установки
Alpha.Server).
Имя файла совпадает с названием модуля. Расширение файлов журнала *.aplog. Размер файла журнала
работы модуля устанавливается вручную в конфигурации каждого модуля и по умолчанию равен «10»
Мбайт. При заполнении заданного размера файла журнала создается другой файл журнала (количество
дополнительных журналов зависит от количества журналов, настроенных при конфигурации модуля), в
который сохранятся все записи текущего журнала. Текущий журнал, в свою очередь, очистится, и запись
работы модуля возобновится в нем. При последующем заполнении текущего файла журнала создается еще
один файл журнала, если в конфигурации модуля он был предусмотрен, либо уже созданный файл журнала
будет перезаписан. После перезагрузки Alpha.Server записи в журнале работы модуля не удаляются, а
добавляются к уже имеющимся в журнале.
ОС Windows
Для просмотра журналов работы модулей Alpha.Server используется сервисное приложение Просмотрщик
лога кадров.
Чтобы просмотреть журнал работы приложений с заданным уровнем трассировки сообщений,
воспользуйтесь приложением EventLogViewer.
ОС Linux
Команда просмотра журнала работы:
journalctl -u alpha.server
26
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 378 ===
5. КОНФИГУРИРОВАНИЕ ALPHA.SERVER
5.4. Пример ручного создания конфигурации
В зависимости от задач, которые предстоит выполнять серверу, определяется модульный состав
Alpha.Server. Ниже приведены несколько примеров:
если необходимо предоставлять данные клиентам по спецификации OPC DA, то в конфигурацию
необходимо добавить модуль OPC DA Server (только в OC Windows);
если необходимо опрашивать некое устройство по спецификации Modbus TCP, то в конфигурацию
необходимо добавить модуль Modbus TCP Master;
если необходимо записывать оперативные данные в сервер истории, то в конфигурацию необходимо
добавить модуль History Module.
Шаги по созданию минимальной конфигурации:
1. Добавьте нужные модули в конфигурацию сервера в зависимости от ваших задач.
2. Чтобы модули начали функционировать, переведите общий параметр модулей Активность в значение
«Да».
3. Настройте общие и дополнительные параметры модулей (стр. 24).
4. Чтобы сервер оперировал данными потребуются сигналы, которые являются контейнерами для
данных. Создайте нужное количество сигналов определенного типа (стр. 34).
5. Чтобы более подробно описать характеристики сигналов или поставить сигналы на обслуживание
какому-либо модулю, добавьте для сигналов свойства (стр. 35). Примеры свойств сигналов:
чтобы детально описать сигнал, определите для него свойство 101 (Description);
если сигнал отражает значение физического параметра, то для него можно определить свойство
100 (Eunit), которое будет отражать единицы измерения;
чтобы поставить сигнал на обслуживание некоторому модулю, настройте привязку через
строковое свойство 5000 (Address);
чтобы настроить сигналу сохранение значений в историю, добавьте свойства 9001 и 9002.
ОБРАТИТЕ ВНИМАНИЕ
Чтобы изменения вступили в силу, после всех изменений конфигурации необходимо перезапустить
Alpha.Server.
Пример добавления и активация модуля
Чтобы OPC DA клиенты получили возможность подключаться к Alpha.Server и запрашивать от него данные
по спецификации OPC DA, необходимо добавить и настроить модуль OPC DA Server:
1. Перейдите на закладку Модули в левой области Конфигуратора.
2. Заблокируйте корень дерева модулей с помощью инструмента
или команды Заблокировать
ветку меню Блокировки. Вид заблокированного дерева модулей представлен на рисунке ниже.
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
27

=== Page 379 ===
5. КОНФИГУРИРОВАНИЕ ALPHA.SERVER
3. Из списка модулей добавьте модуль OPC DA Server.
Добавленный модуль появится в дереве модулей.
4. Активируйте модуль OPC DA Server. На закладке Параметры узла конфигурации модуля в группе
Общие для параметра Активность установите значение «Да».
5. Разблокируйте корень дерева модулей с помощью инструмента
или команды Снять блокировку
меню Блокировки. В появившемся окне сохраните внесенные изменения.
Пример добавления сигнала и его свойств
В рамках примера будет добавлен сигнал типа UInt2 со свойствами 2 (Value), 3 (Quality), 101
(Description).
Чтобы добавить сигнал в конфигурацию сервера:
1. Перейдите на закладку Сигналы в левой области Конфигуратора.
28
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 380 ===
5. КОНФИГУРИРОВАНИЕ ALPHA.SERVER
2. Из контекстного меню или меню Сигналы выберите необходимый тип сигнала.
Добавленный сигнал появится в дереве сигналов.
3. Чтобы добавить свойства сигналу, нажмите Добавить в области Свойства сигнала.
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
29

=== Page 381 ===
5. КОНФИГУРИРОВАНИЕ ALPHA.SERVER
4. В окне Добавление свойств укажите Номер и Значение для нового свойства. Поле Тип заполнится
автоматически. Настройка свойства 2 (Value) показана на рисунке ниже.
Настройка для свойства 3 (Quality):
Номер - «3 (Quality)»;
Значение - «200».
Настройка для свойства 101 (Description):
Номер - «101 (Description)»;
Значение - «Описание Новый сигнал 1».
Область Свойства сигнала после добавление свойств сигналу показана на рисунке ниже.
Пример просмотра значений сигналов OPC DA клиентом
В рамках примера будут просмотрены значения добавленных сигналов OPC клиентом OpcExplorer.
Чтобы просмотреть значения сигналов:
30
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 382 ===
5. КОНФИГУРИРОВАНИЕ ALPHA.SERVER
1. Подключитесь OPC клиентом к OPC DA серверу Alpha.Server.
2. Перейдите в свойства сигнала «Новый сигнал 1».
5.5. Резервное копирование конфигурации сервера
Создание резервной копии конфигурации Alpha.Server возможно выполнить следующими способами:
автоматически. В автоматическом режиме резервное копирование выполняется в соответствии с
настройками расписания, указанными в файле настроек сервера Alpha.Server.xml (стр. 20).
вручную через приложение Конфигуратор и приложение Управляющий.
Чтобы создать резервную копию конфигурации через сервисное приложение Конфигуратор, в окне
приложения выберите команду Сервер →Создать архивную копию конфигурации.
Чтобы создать резервную копию конфигурации сервера с помощью сервисного приложения Управляющий, в
окне приложения нажмите кнопку Резервное копирование.
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
31

=== Page 383 ===
5. КОНФИГУРИРОВАНИЕ ALPHA.SERVER
Настройки сохранения резервных копий в ручном и в автоматическом режиме задаются в файле настроек
сервера Alpha.Server.xml теге <Backup>:
Path - название каталога, в который сохраняются резервные копии;
Time - время автоматического выполнения резервного копирования;
StorageDepth - длительность хранения резервных копий на диске. Указывается в сутках, значение по
умолчанию «14» суток.
Чтобы восстановить конфигурацию Alpha.Server из резервной копии:
файлу резервной копии задайте имя, указанное в файле Alpha.Server.xml (в папке/директории
установки Alpha.Server) в атрибуте Filename элемента Storage (по умолчанию AlphaServer.cfg);
замените текущий файл конфигурации Alpha.Server.
5.6. Защита от несанкционированного доступа
Установка пароля доступа к Alpha.Server предотвращает следующие несанкционированные действия:
управление сервером или резервной парой серверов через сервисное приложение Управляющий;
модификацию конфигурации через сервисное приложение Конфигуратор;
просмотр статистической информации через сервисное приложение Статистика;
обмен данными с Alpha.AccessPoint.
Операции с паролем доступа (создание/изменение) выполняются в окне Смена пароля, которое запускается
командой меню Сервер →Сменить пароль сервера из сервисного приложении Конфигуратор.
После первого подключения к серверу (не требует ввода пароля) следует назначить пароль через окно Смена
пароля.
32
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 384 ===
5. КОНФИГУРИРОВАНИЕ ALPHA.SERVER
ОБРАТИТЕ ВНИМАНИЕ
Пароль хранится в файле Alpha.Server.xml в зашифрованном виде.
5.7. Шифрование паролей
Пароль доступа к серверу, а также пароли, указываемые в параметрах некоторых модулей, хранятся в
зашифрованном виде. Для шифрования паролей используется ассиметричный алгоритм шифрования RSA с
ключом размером 1024 бита:
введённый пароль шифруется с помощью открытого ключа и сохраняется в зашифрованном виде;
сохранённый пароль расшифровывается только когда он нужен в открытом виде (например, при
сравнении паролей). Расшифровка выполняется с помощью закрытого ключа. Закрытый ключ
зашифрован алгоритмом blowfish и в открытом виде нигде не хранится.
5.8. Контроль целостности конфигурации и БД
При запуске Alpha.Server выполняет проверку целостности конфигурации, а в процессе работы - проверку
целостности БД реального времени в части доступности данных. В случае выявления ошибок информация о
них выводится в системный журнал или журналы работы модулей Alpha.Server. Для получения подробной
информации о сообщениях проверки целостности конфигурации и БД обратитесь в техническую поддержку
АО «Атомик Софт» по электронной почте support@automiq.ru или на сайте support.automiq.ru.
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
33

=== Page 385 ===
6. СИГНАЛЫALPHA.SERVER
6. Сигналы Alpha.Server
Для сбора данных о состоянии технологического процесса и для доставки команд пользователя
оборудованию Alpha.Server использует сигналы. Сигнал – это переменная определённого типа: целое или
вещественное число, логическая переменная, строка.
Сигнал может хранить значение некоторого технологического параметра. Например, давление в
трубопроводе, состояние компрессора или сообщение системы.
Alpha.Server хранит сигналы в виде дерева. Для удобства его структуру можно менять.
6.1. Типы данных
Тип данных сигнала определяет, какое множество значений может принимать технологический параметр,
описываемый данным сигналом. Возможные типы данных Alpha.Server показаны ниже.
Тип
Описание
Допустимые значения
Int1
Знаковое целое 1 байт
[-128; 127]
UInt1
Беззнаковое целое 1 байт
[0; 255]
Int2
Знаковое целое 2 байта
[-32 768; 32 767]
UInt2
Беззнаковое целое 2 байта
[0; 65 535]
Int4
Знаковое целое 4 байта
[-2 147 483 648; 2 147 483 647]
UInt4
Беззнаковое целое 4 байта
[0; 4 294 967 295]
Int8
Знаковое целое 8 байт
[–9 223 372 036 854 775 808; 9 223 372 036 854 775 807]
UInt8
Беззнаковое целое 8 байт
[0; 18 446 744 073 709 551 615]
34
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 386 ===
6. СИГНАЛЫALPHA.SERVER
Тип
Описание
Допустимые значения
Float
Значение с плавающей запятой 4
байта
[±1.5×10-45; ±3.4×1038]. Точность 6-9 цифр
Double
Значение с плавающей запятой 8
байт
[±5.0×10-324; ±1.7×10308]. Точность 15-17 цифр
Bool
Логическое значение
true, false
String
Текстовая строка в кодировке
UTF16
до 2 миллиардов знаков, каждый знак занимает 16 бит
(2 байта)
6.2. Свойства сигналов
Кроме значения технологического параметра, сигнал хранит дополнительную информацию о параметре.
Например, единицы измерения значения (МПа, мм), описание («Давление в трубопроводе», «Уровень в
резервуаре»). Эта информация хранится в свойствах сигнала.
Полный список свойств сигналов Alpha.Server приведен в приложении (стр. 60).
6.3. Статические и динамические сигналы
Все сигналы сервера делятся на 2 типа:
Статические – сохраняются в файл конфигурации AlphaServer.cfg (стр. 22). Инициализирующие
значения статистических сигналов задаются и корректируются с помощью приложения Конфигуратор и
Alpha.DevStudio. Заданные значения устанавливаются сигналам и свойствам при старте сервера. В
случае изменения значений сигналов и свойств с помощью OPC DA клиентов, внесенные изменения
действуют только до перезапуска сервера. OPC DA клиенты могут подписываться только на
именованные свойства сервера. Сервер позволяет подписаться и изменять свойства 2, 3, 4 только с
использованием модуля Write VQT Module.
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
35

=== Page 387 ===
6. СИГНАЛЫALPHA.SERVER
Динамические – создаются ядром сервера или модулями сервера. Динамические сигналы не
сохраняются в конфигурации сервера. Служебные сигналы, созданные модулями и ядром сервера,
позволяют наблюдать за работой сервера или конкретного модуля. Просмотр и изменение сигналов и
свойств возможен только с помощью OPC DA клиентов. Изменения значений динамических сигналов и
свойств действуют только до перезагрузки сервера. После перезапуска сервера сигнал или свойство
принимает исходное значение. Например, динамическим свойством является свойство 5002 (RawValue),
которое создается ядром при взятии сигнала на обслуживание.
6.4. Возможные значения качества сигналов
Достоверность значения технологического параметра определяется исходя из значения свойства 3
(Quality). Качество сигнала является индикатором возможности использования значения сигнала при
оценке оперативной ситуации.
Инициализирующие значения качества сигналов настраиваются в конфигурации Alpha.Server. В случае если
качество не было задано на этапе конфигурирования сигналов, при старте сервера ядро устанавливает всем
сигналам качество OUT_OF_SERVICE. Указанное значение качества говорит о том, что сигнал не поставлен
на обслуживание ни одним модулем. Далее сигналы передаются на обслуживание модулям и качество
выставляется обслуживающими модулями. Качество сигнала может изменяться при пересчете значения
сигнала.
Качество сигналов можно просмотреть, подключившись к Alpha.Server с помощью OPC DA клиента.
Значение качества сигнала может быть установлено модулями сервера на основании данных и алгоритмов их
работы в соответствии со спецификацией OPC DA 2.05a.
Значение сигнала достоверно, если качество имеет одно из следующих значений:
Значение
Описание
Возможные причины
GOOD (192)
Значение получено от устройства
(источника данных) с хорошим качеством
Значение установлено одним из модулей
или задано в конфигурации сервера
CALCULATED
(200)
Значение получено в результате
вычислений
Качество всех аргументов достоверное
(>=192) и не возникло переполнений
LOCAL_
OVERRIDE
(216)
Значение изменено пользователем
вручную
Значение изменено пользователем по OPC
Значение сигнала недостоверно и должно игнорироваться, если качество имеет одно из следующих значений:
Значение
Описание
Возможные причины
BAD (0)
Данные получены с плохим
качеством
В регистре статуса сигнала старший бит не
равен нулю
CONFIG_ERROR
(4)
Неверно заданы параметры сигнала
Неверный адрес сигнала. Например: одно из
полей структуры адреса задано неверно.
Расширенную информацию можно получить
из журнала работы модуля
36
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 388 ===
6. СИГНАЛЫALPHA.SERVER
Значение
Описание
Возможные причины
NOT_
CONNECTED (8)
Модуль, обслуживающий сигнал, не
подключен к источнику данных
Соединение с подчиненной станцией не
установлено. Например, последовательный
порт, через который поступает значение
сигнала, не открыт
DEVICE_
FAILURE (12)
Модулю, обслуживающему сигнал, не
удалось подключиться к источнику
данных
Не удалось открыть устройство,
осуществляющее прием/передачу данных.
Например: не удалось открыть
последовательный порт, через который
получается значение сигнала
SENSOR_
FAILURE (16)
Устройство (источник данных), с
которого должно быть получено
значение сигнала, неисправно. От
устройства получено значение
сигнала, выходящее за допустимые
пределы
Датчик неисправен
LAST_KNOWN
(20)
Связь с устройством (источником
данных), поставляющим значение
сигнала, потеряна. Отображается
последнее известное значение
параметра
Отсутствует связь с устройством
COMM_FAILURE
(24)
Не удалось установить связь с
устройством (источником данных), от
которого должно быть получено
значение сигнала
Отсутствует связь с устройством, который
должен поставлять сигнал; Например, КП
номер 3, связанный с сигналом, отсутствует
на связи
OUT_OF_
SERVICE (28)
Сигнал не обслуживается
Сигнал не поставлен на обслуживание ни
одним активным (запущенным) модулем.
Например: адрес сигнала содержит неверный
тип протокола (ни один из запущенных
модулей не поддерживает указанный
протокол)
WAITING_FOR_
INITIAL_DATA (32)
C момента инициализации
Alpha.Server значение, качество и
метка времени сигнала не
изменялись. При этом сигналу
установлено значение «0»
Данные от контроллера не приходят
UNCERTAIN (64)
Данные не получены
Связь с устройством (источником данных),
поставляющим значение сигнала,
установлена, но данные еще не получены
EGU_EXCEEDED
(84)
(Engineering Units Exceeded).
Возвращаемое значение выходит за
границы, определенные для этого
параметра
Значение сигнала вышло за рамки при
пересчете
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
37

=== Page 389 ===
6. СИГНАЛЫALPHA.SERVER
Значение
Описание
Возможные причины
SUB_NORMAL
(88)
Значение вычислено из множества
значений и не все из них имеют
качество GOOD
Значение сигнала вычислено на основе
нескольких сигналов и не все сигналы имеют
достоверное качество
6.5. Адресация сигналов
Основным назначением Alpha.Server является обмен технологическими данными со сторонними OPC
серверами по спецификации OPC DA v.2.05a, а также с устройствами телемеханики и станционной
автоматики по следующим коммуникационным протоколам и технологиям:
ГОСТ Р МЭК 60870-5-104;
Modbus TCP;
Modbus RTU;
SNMP;
SQL-запросы;
ICMP.
Сбор, передача данных и выдача управляющих воздействий осуществляется с помощью технологических
сигналов Alpha.Server. Для привязки сигнала к коммуникационным модулям Alpha.Server используется
свойство 5000 (Address). Формат адреса сигнала определяется используемым протоколом передачи
данных. Каждый сигнал может быть привязан к одному или нескольким коммуникационным модулям
Alpha.Server. В случае связи с несколькими модулями количество адресов сигнала совпадает с
количеством модулей.
Адрес сигнала содержится в свойстве 5000 (Address). Указанное свойство может содержать данные только
строкового типа. Адрес сигнала является статическим свойством и создается пользователем вручную.
Синтаксис установки свойства 5000 (Address) приведен в документах на конкретные модули.
Создание и настройка адресов технологических сигналов Alpha.Server выполняется с помощью сервисного
приложения Конфигуратор.
6.6. Настройка ведения детального журнала по
выбранному сигналу
Данная функция позволяет вести детальный журнал изменений сигналов. По умолчанию, ведение
детального журнала по изменениям сигналов отключено. Ведение детального журнала настраивается в
сервисном приложении Конфигуратор. Ведение детального журнала изменений сигналов реализовано в
следующих модулях:
IEC-104 Master;
TCP Server Module;
HUB Module;
OPC DA Server;
OPC DA Client.
Чтобы настроить сигналу ведение детального журнала, в окне Добавление свойства введите номер свойства -
7000, тип данных - bool и значение - «True». Чтобы отключить функцию ведения детального журнала, в окне
Добавление свойства укажите значение «False» или удалите свойство 7000.
38
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 390 ===
6. СИГНАЛЫALPHA.SERVER
Чтобы просмотреть детальный журнал изменений по выбранному сигналу, используйте сервисное
приложение Просмотрщик лога кадров.
На рисунке ниже показаны фрагменты журнала работы модуля TCP Server Module. На рисунке сверху
показан лог с включенной функцией ведения детального журнала изменений для сигнала
«LU1.SW1.Signal2», снизу - с выключенной функцией.
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
39

=== Page 391 ===
7. СБОР ДАННЫХ
7. Сбор данных
Сбор технологических данных происходит при опросе коммуникационных устройств, ПЛК и сторонних
серверов. Схема сбора данных и передачи их в ядро Alpha.Server показана на рисунке ниже.
Alpha.Server способен собирать данные по различным коммуникационным протоколам и спецификациям.
Чтобы настроить Alpha.Server на сбор данных:
1. Добавьте в состав конфигурации модули, которые соответствуют выбранным
протоколам/спецификациям, и активируйте их.
2. Настройте модули на сбор данных. Как настроить модули см. в документе на соответствующий
модуль.
40
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 392 ===
8. ЛОГИЧЕСКАЯ ОБРАБОТКА ДАННЫХ
8. Логическая обработка данных
Логическая обработка данных, собранных с коммуникационных устройств, ПЛК и сторонних серверов - это
одна из основных задач Alpha.Server.
Логические вычисления, такие как пересчет значений сигналов (стр. 41) и перекладка данных между
сигналами (стр. 48), выполняются ядром Alpha.Server и доступны без использования модуля логики. Для
прочих вычислений в составе конфигурации Alpha.Server необходим модуль Logics Module.
Основные отличия логической обработки данных в ядре и модулем логики:
1. Пересчет значений сигналов и перекладка данных между сигналами не реализуется с помощью
модуля вычислений.
2. Простые логические вычисления, пересчет значений сигналов и перекладка данных между сигналами,
происходят синхронно, а логические вычисления с помощью модуля логики - асинхронно.
Синхронный подход обработки данных выражается в том, что пока ядро сервера производит логическую
обработку данных, оно не сможет выполнять больше никаких других функций. При асинхронном подходе
обработки данных модуль логики выполняет вычисления всех значений сигналов параллельно без участия
ядра сервера, в ядро записывается уже обработанное модулем значение сигнала.
Чтобы настроить логическую обработку данных в ядре Alpha.Server, добавьте в сигнал свойства,
отвечающие за пересчет значений или перекладку данных между сигналами.
8.1. Пересчет значений сигналов
Данные, поступающие с подчиненных станций в Alpha.Server, представляют собой физические величины.
Для корректной обработки входящих значений параметров физические величины, полученные с физических
устройств измерения, переводятся в инженерные. Для подачи управляющих воздействий с пункта
управления инженерные величины переводятся в физические. Пересчет выполняется с помощью встроенной
в ядро Alpha.Server функции пересчета.
Физическое значение параметра записывается в свойство сигнала 5002 (Raw Value). Инженерное значение
параметра содержится в свойстве сигнала 2 (Value). Свойство 5002 (Raw Value) создается ядром
Alpha.Server при постановке сигнала на обслуживание коммуникационным модулем.
Функция пересчета физического значения в инженерное активируется, если изменилось значение свойства
5002 (Raw Value) или значение любого из свойств пересчёта (стр. 41) (например, с помощью OPC клиента).
Полученное в процессе пересчета результирующее значение будет записано в свойство 2 (Value). Пересчет
инженерного значения в физическое производится при изменении свойства 2 (Value). Результат пересчета
будет записан в свойство 5002 (Raw Value).
В Alpha.Server возможен пересчет следующими методами:
Линейный пересчет (стр. 42);
Линейный пересчет с изломом (стр. 46);
Инверсия битовых сигналов (стр. 48).
8.1.1. Настройка пересчета значений сигналов
Для настройки пересчета необходимо создать набор свойств, в которых задаются параметры пересчета. Для
каждого вида пересчета предназначен определенный набор свойств. Список свойств пересчета представлен
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
41

=== Page 393 ===
8. ЛОГИЧЕСКАЯ ОБРАБОТКА ДАННЫХ
в таблице ниже.
ID
Тип
Короткое имя
Описание
5100
double
RecalcRawLow
Нижняя граница физического значения
5101
double
RecalcRawMiddle
Граница излома физического значения
5102
double
RecalcRawHigh
Верхняя граница физического значения
5103
double
RecalcValLow
Нижняя граница инженерного значения
5104
double
RecalcValMiddle
Граница излома инженерного значения
5105
double
RecalcValHigh
Верхняя граница инженерного значения
5106
bool
RecalcTruncate
Усекать значение по границе пересчета и добавлять в качество
флаги усечения (LIMIT_LOW или LIMIT_HIGH)
5107
bool
RecalcSetFailureQuality
При усечении по границе пересчета выставлять SENSOR_
FAILURE
5108
bool
RecalcInvert
Инвертировать логическое значение. Действует только для
сигналов с типом bool.
Если сигнал имеет свойство 5002 (Raw Value), но не имеет свойств пересчета, то физическое значение из
свойства 5002 (Raw Value) записывается в инженерное значение (свойство 2 (Value)).
8.1.2. Линейный пересчет
Линейный пересчет физического значения в инженерное и в обратном направлении значений выполняется по
линейной зависимости. На рисунке ниже показан график линейной функции, отражающий зависимость
физических значений параметров от инженерных значений и наоборот.
Линейная функция имеет вид:
y=kx+b
42
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 394 ===
8. ЛОГИЧЕСКАЯ ОБРАБОТКА ДАННЫХ
Для создания функций линейного пересчета при старте Alpha.Server добавьте в конфигурацию сигнала
следующие свойства:
5100 (нижняя граница физического значения);
5102 (верхняя граница физического значения);
5103 (нижняя граница инженерного значения);
5105 (верхняя граница инженерного значения).
При отсутствии указанных свойств значение сигнала не пересчитывается.
Линейный пересчет значений выполняется согласно следующей последовательности действий:
1. Вычисляются угловой коэффициент и начальная ордината прямой. Линейная функция имеет вид:
y=kx+b
где:
k – угловой коэффициент;
b – начальная ордината прямой.
Искомые величины вычисляются с использованием формулы:
где:
x – физическое значение параметра;
y – инженерное значение параметра;
x_1, x_2 – координаты первой точки;
y_1, y_2 – координаты второй точки.
Координатами точек по оси ординат являются значения нижней и верхней границы инженерного значения
параметра (свойства 5103, 5105). Координатами точек по оси абсцисс являются значения нижней и
верхней границы физического значения параметра (свойства 5100, 5102).
С использованием найденных величин будет сформировано уравнение прямой.
2. Согласно сформированному уравнению прямой строится график линейной функции в декартовой
системе координат.
3. На основе построенного графика выполняется преобразование физического значения параметра в
инженерное и наоборот.
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
43

=== Page 395 ===
8. ЛОГИЧЕСКАЯ ОБРАБОТКА ДАННЫХ
ПРИМЕР
Линейный пересчет значения сигнала
В конфигурацию сигнала добавлены свойства для линейного пересчета значения сигнала.
На рисунке ниже показан график с точками, которые являются границами пересчета. Первая точка
имеет координаты, равные нижним границам физического и инженерного значений. Вторая точка
имеет координаты, равные верхним границам физического и инженерного значений.
Из графика видно, что если физическое значение сигнала равно «30», то после пересчета инженерное
значение сигнала станет равно «46».
Если физическое значение сигнала выходит за пределы границ пересчета, то пересчет значения
сигнала продолжает осуществляться по линейной зависимости (например, физическое значение
сигнала «80» будет пересчитано в инженерное значение сигнала «76»). Чтобы исключить пересчет
значений сигналов за пределами границы пересчета, используйте свойство 5106 (RecalcTruncate).
Чтобы настроить линейный пересчет значений сигналов с обрезкой значений, добавьте в конфигурацию
сигнала свойства 5106 (RecalcTruncate) и 5107 (RecalcSetFailureQuality).
Чтобы значение, которое получится в результате пересчета, проверялось на принадлежность заданному
диапазону пересчета, добавьте сигналу свойство 5106 (RecalcTruncate).
На рисунке ниже показан график из примера линейного пересчета сигнала, но с выделенным участком
прямой, за рамки которого не должно выходить результирующее значение при пересчете. Участок прямой
выделен зеленым цветом.
44
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 396 ===
8. ЛОГИЧЕСКАЯ ОБРАБОТКА ДАННЫХ
Если в результате пересчета полученное значение сигнала со свойством 5106 (RecalcTruncate) вышло за
пределы установленных границ, оно приравнивается к ближайшей границе пересчета. Качество сигнала
устанавливается LIMIT_LOW, если значение было усечено до нижней границы, или LIMIT_HIGH, если
значение было усечено до верхней границы.
Значение качества увеличивается на «1» в случае усечения по нижней границе и на «2» – по верхней. Если
полученное значение находится в пределах границ пересчета, то качество сигнала не изменяется. На рисунке
ниже показаны значения качества сигнала «Новый сигнал 3» (значения в сигнал поступают от DA-клиента).
Чтобы усеченным значеням сигналов выставлялось плохое качество, добавьте сигналу свойство 5107
(RecalcSetFailureQuality).
Если значение сигнала было усечено до нижней границы, сигналу выставляется качество Sensor Failure (Low).
Если значение было усечено до верхней границы, сигналу устанавливается качество Sensor Failure (High).
Усеченным значениям выставляется плохое значение качества, только если в сигнал добавлено свойство
5106 (RecalcTruncate).
На рисунке ниже показаны значения качества сигнала «Новый сигнал 3».
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
45

=== Page 397 ===
8. ЛОГИЧЕСКАЯ ОБРАБОТКА ДАННЫХ
8.1.3. Линейный пересчет с изломом
Линейный пересчет с изломом физического значения в инженерное и в обратном направлении значений
выполняется по двум линейным зависимостям: до точки излома и после точки излома. Появление излома в
прямой при пересчете объясняется наличием у некоторых приборов измерений двух диапазонов оцифровки.
На рисунке ниже показан график, построенный с учетом двух линейных зависимостей. Аналогично
линейному пересчету график отражает зависимость физических значений параметров от инженерных
значений и наоборот.
Линейная функция на одном участке прямой имеет вид:
y=kx+b
На другом участке прямой вид:
y=mx+n
Для создания функций линейного пересчета c изломом при старте Alpha.Server, добавьте в конфигурацию
сигнала следующие свойства:
46
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 398 ===
8. ЛОГИЧЕСКАЯ ОБРАБОТКА ДАННЫХ
5100 (нижняя граница физического значения);
5101 (граница излома физического значения);
5102 (верхняя граница физического значения);
5103 (нижняя граница инженерного значения);
5104 (граница излома инженерного значения);
5105 (верхняя граница инженерного значения).
При отсутствии указанных свойств значение сигнала не пересчитывается.
Линейный пересчет с изломом представляет собой линейный пересчет на каждом участке прямой.
ПРИМЕР
Линейный пересчет значения сигнала с изломом
В конфигурацию сигнала добавлены свойства для линейного пересчета значения сигнала.
На рисунке ниже показан график, вторая точка которого является точкой излома, первая и третья
точки являются границами пересчета.
Из графика видно, что если физическое значение сигнала равно «85», то после пересчета инженерное
значение сигнала станет равно «60».
Если физическое значение сигнала выходит за пределы границ пересчета, то пересчет значения
сигнала продолжает осуществляться по линейной зависимости (например, физическое значение
сигнала «133» будет пересчитано в инженерное значение сигнала «72»). Чтобы исключить пересчет
значений сигналов за пределами границы пересчета, используйте свойство 5106 (RecalcTruncate).
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
47

=== Page 399 ===
8. ЛОГИЧЕСКАЯ ОБРАБОТКА ДАННЫХ
Чтобы настроить линейный пересчет значений сигналов с изломом и с обрезкой значений, добавьте в
конфигурацию сигнала свойства 5106 (RecalcTruncate) и 5107 (RecalcSetFailureQuality). Свойства
работают также, как в линейном пересчете значений сигналов.
На рисунке ниже показан график из примера линейного пересчета значения сигнала с изломом, но с
выделенным участком кривой, за рамки которой не должно выходить результирующее значение при
пересчете. Участок кривой выделен зеленым цветом.
8.1.4. Инверсия битовых сигналов
Действует только для сигналов, имеющих канонический тип bool (дискретный сигнал). Если сигнал является
логическим, свойства пересчета не рассматриваются, при старте Alpha.Server создается функция
инверсного пересчета. Функция создается, если в конфигурации сигнала присутствует свойство 5108
(RecalcInvert).
При наличии у сигнала свойства 5108 (RecalcInvert) исходное физическое значение сигнала, записанное в
свойстве 5002 (Raw Value), инвертируется. Если значение сигнала было равно «true», оно преобразуется в
«false» и наоборот. Преобразованное значение записывается в свойство 2 (Value). Аналогичное правило
действует для преобразования инженерных значений сигналов.
При отсутствии свойства 5108 (RecalcInvert) у сигнала значение не инвертируется и записывается в
свойство 5002 (Raw Value)/ 2 (Value) в исходном виде.
8.2. Перекладка значений сигналов
Для сигналов, поступающих с подчинённых станций (сигналы-источники), можно настроить перекладку
данных в другие сигналы Alpha.Server (сигналы-приёмники).
Перекладка - это один из видов вычислений, выполняемых ядром Alpha.Server. Перекладка позволяет
копировать:
значение сигнала (Value);
качество сигнала (Quality);
метка времени сигнала (Timestamp);
биты сигнала (часть значения сигнала).
48
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 400 ===
8. ЛОГИЧЕСКАЯ ОБРАБОТКА ДАННЫХ
Допускается перекладывать в один сигнал данные с разных сигналов (комбинированная перекладка).
Чтобы настроить перекладку, добавьте сигналу-приёмнику сигнальное свойство 6500 (тип string).
8.2.1. Перекладка значения
Перекладка значения сигнала позволяет скопировать значение свойства Value (2) сигнала-источника в
сигнал-приёмник.
ОБРАТИТЕ ВНИМАНИЕ
Тип сигнала-приёмника должен совпадать с типом сигнала-источника.
Перекладка значений доступна для сигналов всех типов. Перекладка в сигнал-приёмник выполняется
синхронно с изменением сигнала-источника.
Чтобы настроить перекладку значения:
1. Добавьте сигналу-приёмнику свойство 6500.
2. В значении свойства укажите привязку к сигналу-источнику:
{value=(тег_сигнала-источника)}
Результаты перекладки:
качество сигнала-приёмника:
GOOD (192), если значение сигнала-источника достоверно;
UNCERTAIN:SUB_NORMAL (88), если значение сигнала-источника недостоверно;
метка времени сигнала-приёмника устанавливается равной метке времени сигнала-источника.
8.2.2. Полная перекладка
Полная перекладка позволяет скопировать свойства Value (2), Quality (3) и Timestamp (4) сигнала-
источника в сигнал-приёмник.
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
49

=== Page 401 ===
8. ЛОГИЧЕСКАЯ ОБРАБОТКА ДАННЫХ
Полная перекладка может потребоваться, когда, например, необходимо VQT-значения, пришедшее с
коммуникационного модуля, записать в несколько сигналов. В этом случае настраиваются один сигнал-
источник на получение данных от модуля и несколько сигналов-приёмников для дублирования записи
данных в них.
ОБРАТИТЕ ВНИМАНИЕ
Тип сигнала-приёмника должен совпадать с типом сигнала-источника.
Перекладка значений доступна для сигналов всех типов. При изменении значения одного из VQT-свойств
сигнала-источника изменяется значение соответствующего свойства сигнала-приёмника.
Чтобы настроить перекладку значения:
1. Добавьте сигналу-приёмнику свойство 6500.
2. В значении свойства укажите привязку к сигналу-источнику:
{vqt=(тег_сигнала-источника)}
Результаты перекладки:
значение (Value) сигнала-приёмника устанавливается равным значению сигнала-источника;
качество (Quality) сигнала-приёмника устанавливается равным качеству сигнала-источника;
метка времени (Timestamp) сигнала-приёмника устанавливается равной метке времени сигнала-
источника.
8.2.3. Перекладка качества
Перекладка качества позволяет устанавливать сигналу-приёмнику значение свойства Quality (3)
посредством изменения значения сигнала-источника («true»/«false»).
Тип сигнала-источника должен быть bool. Тип сигнала-приёмника может быть любой.
Чтобы настроить перекладку значения:
50
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 402 ===
8. ЛОГИЧЕСКАЯ ОБРАБОТКА ДАННЫХ
1. Добавьте сигналу-приёмнику свойство 6500.
2. В значении свойства укажите привязку к сигналу-источнику:
{quality=(тег_сигнала-источника)}
Результаты перекладки:
значение (Value) сигнала-приёмника остается неизменным;
качество (Quality) сигнала приемника может быть следующим:
остается неизменным, если сигнал-приёмник имеет пустое значение (например, после запуска
Alpha.Server);
UNCERTAIN:SUB_NORMAL (88), если значение сигнала-источника недостоверно;
GOOD (192), если значение сигнала-источника достоверно и равно «true»;
BAD (0), если значение сигнала-источника достоверно и равно «false».
метка времени (Timestamp) сигнала-приёмника остается неизменной.
8.2.4. Перекладка битов
Перекладка бита или группы битов позволяет получить значение (Value) нужных битов из значения сигнала-
источника.
Перекладка бита (группы битов) может потребоваться, когда, например, в сигнале-источнике хранится не
собственное значение, а наборы битов (битовая маска) и необходимо получить значение одного конкретного
бита (группы битов) из маски, который будет записан в сигнал-приёмник. На рисунке ниже показано, как
значение третьего бита сигнала-источника передалось в сигнал-приёмник.
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
51

=== Page 403 ===
8. ЛОГИЧЕСКАЯ ОБРАБОТКА ДАННЫХ
ОБРАТИТЕ ВНИМАНИЕ
При перекладке одного бита: тип сигнала-приёмника может быть bool или любым целочисленным
типом. Тип сигнала-источника может быть любым, кроме string.
ОБРАТИТЕ ВНИМАНИЕ
При перекладке группы битов: типы сигнала-приёмника и сигнала-источника могут быть любого
целочисленного типа. Тип сигнала-приёмника и сигнала-источника должны быть одного знака.
Перекладка в сигнал-приёмник выполняется синхронно с изменением сигнала-источника.
ОБРАТИТЕ ВНИМАНИЕ
Значения группы битов записываются в сигнал-приёмник в десятичном виде.
Чтобы настроить перекладку битов:
1. Добавьте сигналу-приёмнику свойство 6500.
2. В значении свойства укажите привязку к сигналу-источнику (параметр vqt - для полной перекладки,
параметр value - для перекладки только значений битов):
{vqt=(тег_сигнала-источника) bit=(номер_бита) count=(количество_битов)}
{value=(тег_сигнала-источника) bit=(номер_бита) count=(количество_битов)}
Где bit - номер бита сигнала-источника, с которого будет начинаться отсчет количества битов,
указанных в параметре count.
ОБРАТИТЕ ВНИМАНИЕ
Нумерация битов ведется с «0», где «0» соответствует младшему биту.
На рисунке ниже показана настройка перекладки VQT-значений только второго бита сигнала «sValue» в
сигнал-приёмник.
52
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 404 ===
8. ЛОГИЧЕСКАЯ ОБРАБОТКА ДАННЫХ
Если при перекладке одного бита необходимо инвертировать полученное значение перед записью в сигнал-
приёмник, то используйте параметр invert (возможные значения параметра: «1» (true) или «0» (false)).
{vqt=(sValue) bit=(1) count=(1) invert=(1)}
В результате перекладки:
значение сигнала-приёмника устанавливается равным значению указанного бита в значении сигнала-
источника;
качество сигнала-приёмника:
GOOD (192), если значение сигнала-источника достоверно;
UNCERTAIN:SUB_NORMAL (88), если значение сигнала-источника недостоверно;
качество сигнала-приёмника устанавливается равным качеству сигнала-источника, если
настроена полная перекладка битов;
метка времени сигнала-приёмника устанавливается равной метке времени сигнала-источника.
Перекладка битов не выполняется и в журнал сообщений выдаются соответствующие сообщения, если:
число (count + bit) больше размера типа сигнала-источника;
число count больше размера типа сигнала-приёмника;
несовпадение наличия знака в типе сигнала-источника и сигнала-приёмника.
8.2.5. Комбинированная перекладка
Комбинированная перекладка позволяет получать данные с нескольких сигналов параллельно и записывать
в один сигнал.
Комбинированная перекладка может потребоваться, когда, например, по коммуникационному протоколу
значения Value и Quality поступают в разные сигналы. Чтобы получить единое значение для сигнала
используется комбинированная перекладка (значение сигнала берётся из одного сигнала, а качество - из
другого).
Возможны следующие варианты комбинаций:
перекладка значения и установка качества. Значение свойства 6500:
{value=(тег_сигнала-источника)}{quality=(тег_сигнала-источника)}
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
53

=== Page 405 ===
8. ЛОГИЧЕСКАЯ ОБРАБОТКА ДАННЫХ
установка качества и перекладка указанного бита. Значение свойства 6500:
{vqt=(тег_сигнала-источника) bit=(номер_бита) count=(количество_битов)}{quality=(тег_
сигнала-источника)}
Определение итогового качества сигнала-приёмника (при использовании варианта с перекладкой значения и
установкой качества) выполняется по следующим правилам:
по правилам перекладки значения определяется качество сигнала-приёмника;
по правилам перекладки качества определяется качество сигнала-приёмника;
если оба определенных качества достоверны, для сигнала-приёмника устанавливается качество
GOOD (192);
если оба или какой-то один из определенных качеств недостоверно, для сигнала-приёмника
устанавливается наименее достоверное из них.
8.2.6. Относительная адресация при копировании
При работе с однотипными деревьями сигналов использовать абсолютную адресацию неудобно: при
копировании/размножении ветки сигналов необходимо редактировать ссылки на сигналы-источники во всех
скопированных сигналах-приёмниках.
Для быстрого конфигурирования однотипных веток сигналов используйте относительную адресацию, при
которой ссылки на сигналы-источники определяются относительно сигнала-приёмника. Использование
относительной адресации позволяет:
копировать ветки сигналов без корректировки ссылок на сигналы-источники;
изменять названия узлов дерева сигналов без нарушения логики работы функции копирования.
Чтобы настроить относительную адресацию при копировании, укажите в значении свойства 6500 сигнала-
приёмника запись следующего формата:
#<N>.<имя_сигнала-источника>
где #<N> - обращение к N-ому уровню дерева, на котором расположен сигнал-источник. Отсчет уровней
ведётся от сигнала-приёмника, уровень которого является нулевым. Количество уровней неограниченно (от 0
до ∞).
Примеры обращений к сигналу-источнику:
#0.<имя_сигнала-источника> - обращение к сигналу-источнику, расположенному на уровень ниже
сигнала-приёмника;
54
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 406 ===
8. ЛОГИЧЕСКАЯ ОБРАБОТКА ДАННЫХ
#1 - обращение к сигналу-источнику, расположенному на уровень выше сигнала-приёмника;
#1.<имя_сигнала-источника> - обращение к сигналу-источнику, расположенному в одном узле с
сигналом-приёмником;
#2 - обращение к сигналу-источнику, расположенному на два уровня выше сигнала-приёмника;
#2.<имя_сигнала-источника> - обращение к сигналу-источнику, расположенному в узле на два
уровня выше сигнала-приёмника:
Использовать относительную адресацию можно для всех видов копирования значений сигнала.
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
55

=== Page 407 ===
8. ЛОГИЧЕСКАЯ ОБРАБОТКА ДАННЫХ
Пример использования относительной адресации
В конфигурацию сервера необходимо добавить сигналы для приёма уведомлений о работе для четырёх
однотипных задвижек:
ZDV_007_12_3;
ZDV_007_12_4;
ZDV_007_12_5;
ZDV_007_12_6.
Для каждой задвижки необходимо добавить сигналы типа uint2, принимающие уведомления об авариях,
режимах и состояниях:
«ALM»;
«Mode»;
«State».
Для каждого сигнала необходимо добавить дочерние сигналы («0» ... «15») типа bool, в которые будут
копироваться значения соответствующих битов родительского сигнала. Родительские сигналы «ALM»,
«Mode», «State» являются сигналами-источниками для дочерних сигналов-приёмников «0» ... «15».
Порядок работы:
1. Создайте узел сигналов (папку) для задвижки ZDV_007_12_3.
2. В узле задвижки ZDV_007_12_3 создайте сигнал-источник «ALM» и задайте для данного сигнала
параметры адреса в свойстве 5000 (Address).
3. Добавьте для сигнала «ALM» дочерние сигналы-приёмники «0» ... «15». Дерево сигналов задвижки
ZDV_007_12_3 имеет вид:
56
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 408 ===
8. ЛОГИЧЕСКАЯ ОБРАБОТКА ДАННЫХ
4. В значении свойства 6500 (Copy Vqt) для каждого сигнала-приёмника укажите параметры
копирования соответствующего бита сигнала-источника с использованием относительной адресации.
Например, для сигнала «ALM.0» свойство 6500 (Copy Vqt) имеет следующее значение:
{vqt=(#1) bit=(0)}
На рисунках ниже приведены примеры настройки сигналов-приёмников «ALM.6» и «ALM.15».
5. После настройки копирования битов сигнала «ALM» с использованием относительной адресации
создайте 2 копии сигнала «ALM» в узле задвижки ZDV_007_12_3 и измените имена сигналов на «Mode» и
«State».
Для скопированных сигналов-источников укажите соответствующие параметры адресов в свойстве 5000
(Address).
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
57

=== Page 409 ===
8. ЛОГИЧЕСКАЯ ОБРАБОТКА ДАННЫХ
6. Создайте 3 копии узла сигналов задвижки ZDV_007_12_3 и задайте им соответствующие имена:
ZDV_007_12_4;
ZDV_007_12_5;
ZDV_007_12_6.
Итоговый вид дерева сигналов показан ниже:
После размножения узлов сигналов задвижек следует изменить только параметры адресов в свойстве
5000 (Address) для сигналов «ALM», «Mode» и «State» каждой задвижки. Никаких изменений в настройке
копирования битов сигналов не требуется.
8.2.7. Пример перекладки
Требуется получить значение давления с КП. Значение давления записывается в сигнал «pressure» (тип
UInt1). Тег сигнала «AK.DMN.R_Bel.LU_21_24.KP_002.pressure».
Чтобы настроить перекладку:
1. Создайте сигнал «p_value» (тип UInt1), в который будет записываться значение сигнала «pressure».
2. Добавьте сигналу «p_value» свойство 6500.
3. Задайте значение свойства 6500:
{value=(AK.DMN.R_Bel.LU_21_24.KP_002.pressure)}
58
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 410 ===
9. ПРЕДОСТАВЛЕНИЕ ДАННЫХ
9. Предоставление данных
Предоставление обработанных данных клиентам, опросчикам и сторонним системам - это одна из основных
задач Alpha.Server. Схема передачи данных из ядра Alpha.Server по запросам клиентов показана ниже.
Alpha.Server способен предоставлять данные по различным коммуникационным протоколам и
спецификациям.
Чтобы настроить Alpha.Server на предоставление данных:
1. Добавьте в состав конфигурации модули, которые соответствуют выбранным
протоколам/спецификациям, и активируйте их.
2. Настройте модули на предоставление данных. Как настроить модули см. в документе на
соответствующий модуль.
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
59

=== Page 411 ===
10. ПРИЛОЖЕНИЯ
10. Приложения
Приложение A: Свойства сигналов Alpha.Server
ID
Тип
Короткое имя
Описание
Стандартные OPC свойства
1
uint4
CDT
CDT (Канонический тип данных)
2
variant
Value
Значение
3
uint4
Quality
Качество
4
STL::time
Timestamp
Метка времени
5
uint4
AccRight
Права доступа. Значения свойства:
1 – readable – чтение;
2 – writable – запись;
3 – readWritable – чтение/запись.
Если значение свойства не задано, то при старте
сервера свойство создаётся динамически со
значением «readWritable»
6
float
ScanRate
Интервал обновления данных с источника в
миллисекундах
100
string
EUnit
Единицы измерения
101
string
Description
Описание сигнала
6500
string
CopyVqt
Записывать в сигнал перекладываемое значение
Коммуникационные модули (адресация сигнала)
5000
string
Address
Адрес сигнала
5001
string
Active
Активный протокол
5002
variant
RawValue
Физическое значение. Свойство создается сервером
динамически. Тип свойства должен соответствовать
каноническому типу сигнала. При создании свойства
активируются функции пересчета в инженерное
значение (свойство 2 Value) и обратно
Пересчет
5100
double
RecalcRawLow
Нижняя граница физического значения
5101
double
RecalcRawMiddle
Граница излома физического значения
5102
double
RecalcRawHigh
Верхняя граница физического значения
60
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 412 ===
10. ПРИЛОЖЕНИЯ
ID
Тип
Короткое имя
Описание
5103
double
RecalcValLow
Нижняя граница инженерного значения
5104
double
RecalcValMiddle
Граница излома инженерного значения
5105
double
RecalcValHigh
Верхняя граница инженерного значения
5106
bool
RecalcTruncate
Усекать значение по границе пересчета и добавлять
в качество флаги усечения (LIMIT_LOW или LIMIT_
HIGH)
5107
bool
RecalcSetFailureQuality
При усечении по границе пересчета выставлять
SENSOR_FAILURE
5108
bool
RecalcInvert
Инвертировать логическое значение. Действует
только для сигналов с типом bool
Ссылки на объекты
6001
string
Полное имя объекта, к которому ведёт данная
ссылка
6002
uint4
Разновидность ссылки. Значения свойства:
«0» - ссылка ведёт исключительно на
указанный объект и не затрагивает его
поддерево сигналов;
«1» - ссылка ведёт на указанный объект и
его поддерево сигналов.
6003
bool
Автораскрытие ссылки. Значения свойства:
«true» - пользователю предоставляется
возможность в DA-клиенте раскрыть поддерево
объекта, на который ведёт ссылка;
«false» - невозможность раскрыть в DA-
клиенте поддерево объекта, на который ведёт
ссылка.
6004
bool
Константность ссылки. Значения свойств:
«true» - сигналы объекта, на который ведёт
ссылка, доступны только для чтения в DA-
клиенте;
«false» - сигналы объекта, на который ведёт
ссылка, доступны для изменений через DA-
клиент.
6005
bool
Свойство модуля OPC AE Server. Если у объекта
определено данное свойство (значение «true»), то
агрегатор области, в которой определена ссылка,
агрегирует также события целевого объекта
Восприимчивость сигнала к изменениям
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
61

=== Page 413 ===
10. ПРИЛОЖЕНИЯ
ID
Тип
Короткое имя
Описание
6100
string
Восприимчивость сигнала к изменениям. Значения
свойства:
«VQChange» – значение сигнала считается
изменившимся, если изменилось значение хотя
бы одного из свойств сигнала:
значение 2 (Value);
качество 3 (Quality);
«AnyChange» – значение сигнала считается
изменившимся, если изменилось значение хотя
бы одного из свойств сигнала:
значение 2 (Value);
качество 3 (Quality);
метка времени 4 (Timestamp);
«Repeat» – значение сигнала считается
изменившимся даже при полном повторе
значений свойств сигнала:
значение 2 (Value);
качество 3 (Quality);
метка времени 4 (Timestamp).
Ведение детального журнала изменений сигналов
7000
bool
Ведение детального журнала изменений сигналов
Резервирование
8000
bool
Опциональная синхронизация при резервировании
Ведение истории
9001
bool
Historizing
Ведение истории
9002
string
HistoryParams
Дополнительные параметры сохранения истории
Модуль Write VQT
10000
bool
EnableWriteVqt
Постановка на обслуживание сигнала модулю Write
VQT
Модуль OPC UA Client
11000
uint1
Преобразование входящих значений типа ByteString в
строку:
«0» – не принимать данные типа ByteString;
«1» - принимать данные типа ByteString и
преобразовывать в строку.
Модуль логики
62
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 414 ===
10. ПРИЛОЖЕНИЯ
ID
Тип
Короткое имя
Описание
777001-777003
string
Используются в конфигурациях, созданных в
Alpha.DevStudio с использованием объектной
модели. Не предназначены для редактирования
пользователем
777005
string
Содержит определения внешних функций
777006
string
Содержит карту дескрипторов сигнатур внешних
функций
777010
string
Формула для вычисления значения сигнала
777011
string
Условие активации процедуры, определенной в
свойстве 777012
777012
string
Код процедуры на языке Alpha.Om. которая
активируется по условию свойства 777011
777013
string
Обработчик, срабатывающий перед отправкой
события. Срабатывает в тот момент, когда по
сигналу уже сгенерировано событие, но само
событие ещё не отправлено клиентам
777015
uint4
Значение таймера (в миллисекундах) для
исполнения процедуры, которая содержится в
свойстве 777016
777016
string
Код процедуры на языке Alpha.Om, исполняемый
циклически по таймеру. Значение таймера
указывается в свойстве 777015
777017
string
Содержит cron-выражение для выполнения
процедуры по расписанию. Код самой процедуры
содержится в свойстве 777018
777018
string
Cодержит код процедуры, которая будет
выполняться по расписанию, заданному в формате
cron-выражения в свойстве 777017
777020-777051
string
Используются в конфигурациях, созданных в
Alpha.DevStudio с использованием объектной
модели. Не предназначены для редактирования
пользователем
Системные (внутренние) свойства
6000
uint4
NotAckEventCount
Количество неквитированных событий
999000
string
ObjectType
Тип объекта
999001
uint4
ObjectCode
Код объекта
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
63

=== Page 415 ===
10. ПРИЛОЖЕНИЯ
ID
Тип
Короткое имя
Описание
999002
string
ObjectSound
Звук объекта
999003
bool
EventsEnabled
Признак генерации событий
999004
string
Conditions
Условия генерации событий
999005
bool
IsAbstract
Тип абстрактный или нет (Экземпляры абстрактного
типа создавать нельзя)
64
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 416 ===
СПИСОК ТЕРМИНОВ И СОКРАЩЕНИЙ
Список терминов и сокращений
OPC (OLE for Process
Control)
Программная технология на базе OLE, ActiveX, COM/DCOM,
предоставляющая набор объектов, используемых в автоматизации
технологических процессов, и интерфейсов доступа к ним.
OPC AE (OLE for Process
Control Alarms&Events)
Интерфейс передачи сообщений OPC, предоставляет функции
уведомления по требованию о различных событиях: аварийные ситуации,
действия оператора, информационные сообщения и другие.
OPC DA (OLE for Process
Control Data Access)
Интерфейс передачи сигналов OPC, описывает набор функций обмена
данными в реальном времени.
OPC UA (OPC Unified
Architecture)
Унифицированная спецификация, определяющая передачу данных в
промышленных сетях.
OPC сервер
Сервер, предоставляющий доступ по интерфейсам OPC к
технологическим данным, полученным по различным каналам, главным
образом, от среднего уровня АСУ ТП. Обычно разрабатывается
производителем контроллеров, автоматики.
TCP (Transmission
Control Protocol)
Протокол управления передачей.
АСУ ТП
Автоматизированная система управления технологическими процессами.
АСУП
Автоматизированная система управления предприятием.
Качество
Характеристика достоверности сигнала.
КП
Контрольный, контролируемый пункт, клапан перепускной.
ОБД
Оперативная база данных параметров.
ОС
Операционная система.
Сигнал
Единица технологической информации, обладающая определённым
набором обязательных и дополнительных свойств.
ALPHA.SERVER. РУКОВОДСТВО АДМИНИСТРАТОРА
65

=== Page 417 ===
Программный комплекс Альфа платформа
Alpha.Server 6.4
Модули NetDiag, NetDiag2
Руководство администратора
Редакция
Соответствует версии ПО
7. Предварительная
6.4.28

=== Page 418 ===
© АО «Атомик Софт», 2015-2026. Все права защищены.
Авторские права на данный документ принадлежат АО «Атомик
Софт». Копирование, перепечатка и публикация любой части или
всего документа не допускается без письменного разрешения
правообладателя.

=== Page 419 ===
Содержание
1. Назначение и принципы работы
4
1.1. Принципы работы
4
1.2. Различия между модулями NetDiag и NetDiag2
4
1.3. Работа в резерве
4
2. Конфигурирование модуля
5
2.1. Добавление сетевого устройства
6
3. Сигналы модуля
8
3.1. NetDiag
8
3.2. NetDiag2
10
3.3. Функции сигналов
10
4. Пример диагностики устройств
13
5. Диагностика работы
14
5.1. Статистика
14
5.2. Журнал работы модуля
14
6. Приложения
15
Приложение A: Запуск модуля NetDiag2 от имени непривилегированного пользователя (для ОС Linux)
15
Список терминов и сокращений
16
ALPHA.SERVER. МОДУЛИ NETDIAG, NETDIAG2. РУКОВОДСТВО АДМИНИСТРАТОРА
3

=== Page 420 ===
1. НАЗНАЧЕНИЕ И ПРИНЦИПЫРАБОТЫ
1. Назначение и принципы работы
Модули NetDiag и NetDiag2 предназначены для диагностики связи с сетевыми устройствами в сетях TCP/IP.
Модули выполняют следующие функции:
проверка возможности доставки IP-пакетов до сетевого устройства (Ping);
определение маршрута следования IP-пакетов до сетевого устройства (TraceRoute).
1.1. Принципы работы
1. Модуль периодически отправляет сетевым устройствам запросы Ping и TraceRoute.
Запросы передаются согласно протоколу ICMPv4, период отправления запросов и список сетевых
устройств указываются при конфигурировании модуля.
2. Результаты запросов модуль записывает в сигналы сервера.
1.2. Различия между модулями NetDiag и NetDiag2
Модуль NetDiag записывает информацию в динамические сигналы сервера.
Динамические сигналы создаются при запуске сервера и не конфигурируются.
Модуль NetDiag2 записывает информацию в статические сигналы сервера.
Статические сигналы создаются и конфигурируются пользователем.
Модуль NetDiag2 следует использовать, если нужно конфигурировать сигналы, используемые
модулем: разместить сигналы в разных ветвях дерева сигналов и/или конфигурировать свойства
сигналов.
1.3. Работа в резерве
В режиме РЕЗЕРВ модули выполняют те же функции, что и в режиме РАБОТА.
4
ALPHA.SERVER. МОДУЛИ NETDIAG, NETDIAG2. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 421 ===
2. КОНФИГУРИРОВАНИЕ МОДУЛЯ
2. Конфигурирование модуля
В составе Alpha.Server одновременно могут работать оба модуля NetDiag и NetDiag2, но не более одного
модуля каждого типа.
Модуль имеет общие и дополнительные параметры.
Параметр
Описание
Имя модуля
Название модуля
Идентификатор
модуля
Идентификатор модуля
Активность
Активность модуля:
«Да» – модуль запущен
«Нет» – модуль остановлен
Уровень
трассировки в
журнал
приложений
Типы сообщений, которые фиксируются в журнал приложений:
«Предупреждения и аварийные сообщения» – логические ошибки, ошибки работы
модуля. Предупреждения содержат некритичные ошибки. Аварийные сообщения
информируют об ошибках, которые влияют на работоспособность службы
«Информационные сообщения» – сообщения, которые показывают основную
информацию о работе модуля
«Отладочные сообщения» – сообщения, которые наиболее детально отражают
информацию о работе модуля
Вышестоящий уровень входит в состав нижестоящего: если выбрано «Информационные
сообщения», то в журнал фиксируются «Предупреждения и аварийные сообщения» и
«Информационные сообщения»
Вести журнал
работы модуля
Ведётся ли журнал работы модуля:
«Да»
«Нет»
Общие параметры
ALPHA.SERVER. МОДУЛИ NETDIAG, NETDIAG2. РУКОВОДСТВО АДМИНИСТРАТОРА
5

=== Page 422 ===
2. КОНФИГУРИРОВАНИЕ МОДУЛЯ
Параметр
Описание
Размер журнала
работы модуля,
МБ
Ограничение на размер файла журнала работы модуля в мегабайтах.
При достижении максимального размера создается новый файл, копия старого файла
хранится на рабочем диске
Количество
дополнительных
журналов
работы
Количество файлов заполненных журналов работы модуля.
Минимальное значение – 1, максимальное – 255
Дополнительные параметры:
Параметр
Описание
Период
диагностики
Ping, мс
Промежуток времени между запросами для проверки наличия соединения с сетевым
устройством в мс
Период
диагностики
TraceRoute,
мс
Промежуток времени между запросами для определения маршрута следования данных
до сетевого устройства в мс
Имя папки
сигналов
модуля
(только у
NetDiag)
Путь к папке в дереве сигналов, в которой модуль создаст динамические сигналы.
Модуль создаст папку при старте сервера. Значение по умолчанию:
«Service.Modules.<Идентификатор_модуля>.Control»
2.1. Добавление сетевого устройства
Чтобы добавить сетевое устройство:
1. В списке модулей модулю NetDiag (или NetDiag2) добавьте сетевое устройство.
6
ALPHA.SERVER. МОДУЛИ NETDIAG, NETDIAG2. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 423 ===
2. КОНФИГУРИРОВАНИЕ МОДУЛЯ
Параметр
Описание
Количество
каналов
Количество каналов, по которому устройству будут отправляться запросы
Псевдоним
Имя устройства, предназначено для удобства поиска нужного устройства в списке
устройств. Должно быть уникальным в пределах списка
2. Для каждого канала укажите значения его параметров.
Параметр
Описание
Псевдоним
Имя канала, предназначено для удобства поиска нужного канала в списке
каналов устройств. Должно быть уникальным в пределах списка
IP/DNS адрес
Адрес канала
Таймаут запросов
диагностики, мс
Максимальное время ожидания ответа устройства на отправленный запрос в
мс. При превышении этого времени результат запроса считается
отрицательным.
Максимальное
количество прыжков
TraceRoute
Максимальное количество промежуточных узлов, через которые проходит
пакет запроса TraceRoute. Значение в диапазоне от «1» до «255».
ALPHA.SERVER. МОДУЛИ NETDIAG, NETDIAG2. РУКОВОДСТВО АДМИНИСТРАТОРА
7

=== Page 424 ===
3. СИГНАЛЫМОДУЛЯ
3. Сигналы модуля
Сигналы модуля используются для:
записи информации о запросах, отправленных сетевым устройствам по каждому каналу
управления запросами, отправляемыми сетевым устройствам по каждому каналу
3.1. NetDiag
Сигналы модуля NetDiag динамические: их создаёт модуль при старте сервера в папке, указанной в
параметрах модуля. Структура папки:
в папке для каждого сетевого устройства создаётся папка; имя папки – псевдоним сетевого
устройства
в папке сетевого устройства для каждого канала создаётся папка; имя папки – псевдоним канала
в папке канала создаются две папки:
«Ping»
«TraceRoute»
8
ALPHA.SERVER. МОДУЛИ NETDIAG, NETDIAG2. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 425 ===
3. СИГНАЛЫМОДУЛЯ
В папках «Ping» и «TraceRoute» создаются сигналы модуля; имя сигнала – название функции,
которую он выполняет (описание функций приведено ниже)
ALPHA.SERVER. МОДУЛИ NETDIAG, NETDIAG2. РУКОВОДСТВО АДМИНИСТРАТОРА
9

=== Page 426 ===
3. СИГНАЛЫМОДУЛЯ
3.2. NetDiag2
Сигналы модуля NetDiag2 статические: их добавляет пользователь при конфигурировании дерева сигналов.
Порядок добавления и конфигурирования сигнала:
1. В дерево сигналов добавьте сигнал.
2. Поставьте сигнал на обслуживание модулю NetDiag2:
2.1. Добавьте сигналу свойство 5000 (Address) типа String.
2.2. В открывшемся окне Редактор адреса добавьте модуль NetDiag2.
2.3. Укажите параметры адреса.
Параметр
Описание
Узел
Сетевое устройство. Выбирается из списка устройств, добавленных модулю
Канал
Канал. Выбирается из списка каналов выбранного сетевого устройства
Режим
Тип запроса:
«Ping»
«TraceRoute»
Функция
Функция сигнала. Список доступных функций зависит от типа сигнала и выбранного
режима
Номер
Номер промежуточного узла в диапазоне от 1 до 255. Указывается только если
выбран режим «TraceRoute» и функция «HopInfo»
3.3. Функции сигналов
Команды
Функция
Тип
сигнала
Описание
Enable
bool
Включение/отключение отправки запросов:
«0» (False) – запросы не отправляются, информационные сигналы принимают
значение качества OPC_QUALITY_OUT_OF_SERVICE;
«1» (True) – запросы отправляются, информационные сигналы принимают
значение качества OPC_QUALITY_GOOD.
Значение при старте сервера – «1»
10
ALPHA.SERVER. МОДУЛИ NETDIAG, NETDIAG2. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 427 ===
3. СИГНАЛЫМОДУЛЯ
Функция
Тип
сигнала
Описание
ResetStat
bool
Сброс значений статистических параметров:
количества успешных запросов («SuccCount»);
количества неуспешных запросов («FailCount»);
текст последней ошибки («LastError»).
Значение при старте сервера – «0» (False)
При изменении значения на «1» (True) выполняется команда и значение сигнала
возвращается в 0 (False)
Информационные сигналы
Функция
Тип
сигнала
Описание
Общие: есть у запросов Ping и TraceRoute
FailCount
uint4
Количество неуспешных запросов с момента запуска модуля.
Обнуляется по команде ResetStat
LastError
string
Текст последней ошибки.
Очищается по команде ResetStat
LastFailDuration
uint4
Последний период времени в секундах, в течение которого запрос
завершился неудачей.
Считается от последнего удачного ответа сетевого устройства до
начала нового запроса, т.е. является суммой ((t+T2)*N), где N –
количество подряд неудачно отправленных запросов
Status
bool
Результат последнего запроса:
0 (False) – запрос завершился ошибкой
1 (True) – запрос завершился успешно
SuccCount
uint4
Количество успешных запросов с момента запуска модуля.
Обнуляется по команде ResetStat
TimeOut
uint4
Период времени в миллисекундах, через который будет
отправлени повторный запрос
TotalFailDuration
uint4
Общий период времени в секундах, в течение которого запросы к
устройству завершались неудачей.
Равно сумме временных промежутков LastFailDuration за время
работы
Ping
Filtered.FailedAttemptsCount
uint1
Количество неуспешных запросов, при превышении которого
статусу FilteredStatus устанавливается значение 0 (False)
Значение при старте сервера – 3
ALPHA.SERVER. МОДУЛИ NETDIAG, NETDIAG2. РУКОВОДСТВО АДМИНИСТРАТОРА
11

=== Page 428 ===
3. СИГНАЛЫМОДУЛЯ
Функция
Тип
сигнала
Описание
Filtered.Status
bool
Отфильтрованное состояние статуса запроса
Filtered.SuccAttemptsCount
uint1
Количество успешных запросов, при превышении которого
статусу FilteredStatus устанавливается значение 1 (True).
Значение по умолчанию – 3
IPaddress
string
IP адрес сетевого устройства
RTTTime
uint4
Последнее зафиксированное время между отправкой запроса и
получением ответа, миллисекунд
Если ответ не получен, сигналу устанавливается качество BAD (0)
TraceRoute
BadAttemptLastReachedHost
string
Последний достигнутый хост при последнем неудачном запросе
HopCount
uint1
Количество промежуточных узлов по пути следования IP-пакета.
Если пакет не достиг целевого узла, устанавливается значение 0
HopInfo<N>
string
Информация о N-м промежуточном узле в формате:
%IP адрес% RTT - %время RTT% мс
,где время RTT – время задержки ответа от промежуточного узла
N. Если информация по промежуточному узлу отсутствует, то
значение сигнала отсутствует
12
ALPHA.SERVER. МОДУЛИ NETDIAG, NETDIAG2. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 429 ===
4. ПРИМЕР ДИАГНОСТИКИ УСТРОЙСТВ
4. Пример диагностики устройств
На рисунке приведена мнемосхема для Alpha.Server, который выполняет диагностику связи с двумя
устройствами.
ALPHA.SERVER. МОДУЛИ NETDIAG, NETDIAG2. РУКОВОДСТВО АДМИНИСТРАТОРА
13

=== Page 430 ===
5. ДИАГНОСТИКА РАБОТЫ
5. Диагностика работы
5.1. Статистика
Статистическая информация о работе модуля отображается на вкладке Статистика сервисного приложения
Конфигуратор, а также в сервисном приложении Статистика.
Чтобы просмотреть параметры статистики модуля, подключитесь к Alpha.Server и выберите модуль в
дереве статистики.
5.2. Журнал работы модуля
Журнал работы модуля сохраняется в файл <имя модуля>.aplog по умолчанию:
в папке C:\Program Files\Automiq\Alpha.Server\Logs, если Alpha.Server функционирует в ОС
Windows;
в директории /opt/Automiq/Alpha.Server/Logs, если Alpha.Server функционирует в ОС семейства
Linux.
Для просмотра журнала работы модуля воспользуйтесь сервисным приложением Просмотрщик лога
кадров.
14
ALPHA.SERVER. МОДУЛИ NETDIAG, NETDIAG2. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 431 ===
6. ПРИЛОЖЕНИЯ
6. Приложения
Приложение A: Запуск модуля NetDiag2 от имени
непривилегированного пользователя (для ОС Linux)
Чтобы модуль NetDiag2 запустился из-под непривилегированной УЗ Linux, настройте системную
переменную net.ipv4.ping_group_range.
ОБРАТИТЕ ВНИМАНИЕ
Если переменная net.ipv4.ping_group_range не задана, то модуль NetDiag2 будет сообщать об ошибке
в журнал приложений.
Чтобы задать системную переменную net.ipv4.ping_group_range, выполните команду:
sysctl -w net.ipv4.ping_group_range="0 4294967"
ОБРАТИТЕ ВНИМАНИЕ
Установленное командой значение переменной будет действовать только до перезапуска ОС.
Чтобы значение переменной устанавливалось при запуске ОС, в директории /etc/sysctl.d создайте файл
99-allow-ping.conf и добавьте в нем строку:
чтобы разрешить запуск модуля всем пользователям:
net.ipv4.ping_group_range = 0
4294967
чтобы разрешить запуск модуля только пользователю, который входит в группу с GID 1002:
net.ipv4.ping_group_range = 1002 1002
ПРИМЕЧАНИЕ
Чтобы узнать GID пользователя, выполните команду:
id
Результат выполнения команды содержит GID:
uid=1001(username) gid=1002(username) группы=1002(username),101(systemd-journal)
ПРИМЕЧАНИЕ
Чтобы перезагрузить новую конфигурацию sysctl, выполните команду:
sudo sysctl --systemS
ALPHA.SERVER. МОДУЛИ NETDIAG, NETDIAG2. РУКОВОДСТВО АДМИНИСТРАТОРА
15

=== Page 432 ===
СПИСОК ТЕРМИНОВ И СОКРАЩЕНИЙ
Список терминов и сокращений
ICMPv4 (Internet Control
Message Protocol)
Протокол межсетевых управляющих сообщений, входящий в стек
протоколов TCP/IP.
SCADA (Supervisory
Control And Data
Acquisition)
Система, обеспечивающая диспетчерское управление и сбор данных.
АСУ ТП
Автоматизированная система управления технологическим процессом.
Дерево сигналов
Структура технологических данных, с которой работают компоненты АСУ
ТП.
Качество сигнала
Свойство сигнала, характеризующее его достоверность.
Маршрутизатор
Сетевое устройство, принимающее и посылающие пакеты данных между
различными сегментами сети.
Модуль
Программный компонент, работающий в составе сервера ввода/вывода,
обеспечивающий некоторую логически законченную функциональность.
Основной функцией модулей сервера ввода/вывода является передача
данных между компонентами АСУ ТП на уровне SCADA-системы.
Сервер ввода/вывода
Компонент сбора данных и управления технологическим оборудованием в
системе автоматизации объектов технологического процесса,
предоставляющий доступ к данным другим компонентам системы.
Сигнал
Объект, являющийся носителем информации при обмене данными между
компонентами АСУ ТП. Сигнал имеет определенный тип и обладает
набором свойств. Основное назначение сигналов хранить значения
реальных физических величин и их свойства: достоверность, параметры
доступа и др.
16
ALPHA.SERVER. МОДУЛИ NETDIAG, NETDIAG2. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 433 ===
Программный комплекс Альфа платформа
Alpha.Server 6.4
Модуль BACnet Client
Руководство администратора
Редакция
Соответствует версии ПО
7. Предварительная
6.4.28

=== Page 434 ===
© АО «Атомик Софт», 2015-2026. Все права защищены.
Авторские права на данный документ принадлежат АО «Атомик
Софт». Копирование, перепечатка и публикация любой части или
всего документа не допускается без письменного разрешения
правообладателя.

=== Page 435 ===
Содержание
1. Назначение и принцип работы
4
1.1. Устройство BACnet
4
1.2. Обмен данными с устройством
5
1.2.1. Обнаружение устройства
5
1.2.2. Получение данных от устройства
5
1.2.3. Подача команд управления
5
1.3. Работа модуля в резерве
6
2. Настройка обмена данными с устройством
7
2.1. Пример устройства
7
2.2. Настройка в Alpha.DevStudio
8
2.2.1. Настройка источника данных
8
2.2.2. Настройка опросчика BACnet
14
2.2.3. Применение конфигурации Alpha.Server
21
2.3. Настройка в Конфигураторе
21
2.3.1. Настройка конфигурации модулей
22
2.3.2. Настройка сигналов
27
2.3.2.1. Добавление сигналов
27
2.3.2.2. Настройка адреса сигнала
27
Получение значения свойства объекта
29
Подача команды управления
31
Настройка сигнала доставки
32
3. Проверка обмена данными
34
4. Диагностика работы
35
4.1. Служебные сигналы
35
4.1.1. Контроль и управление подключаемым источником
35
4.1.2. Управление подпиской на свойства объектов
36
4.1.3. Контроль и управление основными параметрами модуля
37
4.2. Параметры статистики
38
4.2.1. Статистика модуля
38
4.2.2. Статистика источника
39
4.2.3. Статистика устройства
40
4.2.4. Статистика канала
41
4.2.5. Статистика локальных интерфейсов
41
4.3. Журнал работы
42
5. Приложения
44
Приложение A: Строковые идентификаторы объектов и свойств
44
Типы объектов
44
Свойства объекта
44
Приложение B: Протокольные типы
46
Входящие сигналы
46
Исходящие сигналы
47
Приложение C: Значения сигнала доставки
48
Приложение D: Настройка типа устройства в Конфигураторе
49
Импорт типа устройства из файла
50
Ручная настройка типа устройства
51
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
3

=== Page 436 ===
1. НАЗНАЧЕНИЕ И ПРИНЦИП РАБОТЫ
1. Назначение и принцип работы
Модуль BACnet Client предназначен для обмена данными между Alpha.Server и устройствами,
поддерживающими протокол BACnet ([BS EN ISO 16484-5_2014] -- Building automation and control systems
(BACS). Data communication protocol, далее - спецификация BACnet).
Функции модуля BACnet Client:
сбор данных с устройств BACnet и сохранение полученных значений в сигналы Alpha.Server;
подача команд управления устройствам BACnet.
1.1. Устройство BACnet
Устройство BACnet имеет логическую структуру, состоящую из набора объектов BACnet. Полный перечень
объектов приведен в спецификации BACnet. Набор объектов для каждого устройства BACnet индивидуален и
приведен в документации на устройство.
ПРИМЕР
Устройство состоит из набора объектов: «Analog_Input» («AI»), «Analog_Output» («AO»), «Analog_
Value» («AV»), «Binary_Input» («BI»), «Binary_Output» («BO»), «Binary_Value» («BV») и устройство
«DEVICE».
Каждый объект BACnet имеет набор свойств, которые содержат информацию об объекте и управляют его
работой. Полный перечень свойств объектов приведен в спецификации BACnet. Набор используемых
свойств объекта для каждого устройства BACnet индивидуален и приведен в документации на устройство.
4
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 437 ===
1. НАЗНАЧЕНИЕ И ПРИНЦИП РАБОТЫ
ПРИМЕР
Объект «AI» имеет набор свойств: тип объекта «Object_Type», идентификатор объекта «Object_
Identifier», название объекта «Object_Name» и текущее значение «Present_Value». Данный объект
соответствует измеряемой температуре.
1.2. Обмен данными с устройством
Обмен данными между модулем BACnet Client и устройством BACnet выполняется по сети Ethernet
(протокол UDP) в режиме запрос-ответ. Инициатором запроса является модуль BACnet Client. Запросы и
ответы представляют собой кадры данных. Для модуля BACnet Client запрос, отправляемый устройству,
является исходящим кадром, а ответ, полученный от устройства – входящим кадром.
1.2.1. Обнаружение устройства
После запуска модуль BACnet Client начинает поиск в сети устройства BACnet, отправляя запрос
обнаружения устройства Who-Is с заданной периодичностью. После получения от устройства ответа I-Am
устанавливается связь с устройством и модуль готов к обмену данными.
После установления связи с устройством модуль BACnet Client отправляет устройству запросы Who-Is для
подтверждения наличия связии в периоды, когда опрос устройства не ведётся.
1.2.2. Получение данных от устройства
Модуль выполняет опрос устройства циклически с паузой между циклами опроса. Для получения данных от
устройства модуль BACnet Client отправляет устройству запрос ReadPropertyMultiple-Request, содержащий
список свойств, значения которых требуется получить. Для каждого объекта отправляется отдельный
запрос.
От устройства модуль получает ответ ReadPropertyMultiple-ACK, содержащий значения запрошенных свойств.
Полученные значения модуль записывает в сигналы Alpha.Server. Если ответ от устройства не получен за
заданный период ожидания ответа от устройства, то связь с устройством считается потерянной.
1.2.3. Подача команд управления
Подача команды управления - это отправка значения сигнала Alpha.Server в устройство. Команды имеют
более высокий приоритет, чем опрос устройства, поэтому при подаче команды модуль прерывает опрос и
передаёт команду управления устройству.
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
5

=== Page 438 ===
1. НАЗНАЧЕНИЕ И ПРИНЦИП РАБОТЫ
Для отправки значения сигнала Alpha.Server в устройство модуль BACnet Client отправляет устройству
запрос WriteProperty-Request, содержащий свойство объекта и значение, которое требуется записать в
устройство.
От устройства модуль получает ответ WriteProperty-ACK, который в случае успешной записи значения в
устройство не содержит ошибок. Если значение в устройство записать не удалось, то ответ WriteProperty-ACK
содержит информацию об ошибке.
Для команд управления возможна настройка сигналов доставки. Значение сигнала доставки определяет
состояние отправленной команды.
1.3. Работа модуля в резерве
В режиме РЕЗЕРВ модуль BACnet Client не ведёт опрос устройств и не отправляет команды управления, но
отправляет запросы обнаружения устройства Who-Is и принимает входящие уведомления I-Am.
6
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 439 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
2. Настройка обмена данными с устройством
Настройка обмена данными между Alpha.Server и устройством BACnet может быть выполнена следующими
способами:
в среде разработки Alpha.DevStudio (стр. 8);
в сервисном приложении Конфигуратор (стр. 21).
Чтобы настроить обмен данными между Alpha.Server и устройством BACnet, необходимы следующие
исходные данные:
1. Для настройки параметров устройства BACnet в конфигурации - идентификатор устройства.
Информация об устройстве содержится в свойствах обязательного для всех устройств объекта
«Device». Идентификатор устройства - значение свойства «Object_Identifier» объекта «Device».
2. Для настройки адресов сигналов в карте адресов или редакторе адреса:
2.1. Идентификатор типа объекта. Для настройки адреса сигнала можно использовать одно из
обозначений типа объекта:
целочисленный идентификатор типа объекта - указан в спецификации BACnet (стр. 690);
строковый идентификатор - для некоторых типов объектов модулем BACnet Client
поддержаны строковые идентификаторы (стр. 44).
2.2. Номер экземпляра объекта. Содержится в значении свойства «Object_Identifier» объекта.
2.3. Идентификатор свойства объекта. Для настройки адреса сигнала можно использовать одно из
обозначений свойства объекта:
целочисленный идентификатор свойства объекта - указан в спецификации BACnet (стр. 694);
строковый идентификатор - для некоторых свойств объектов модулем BACnet Client
поддержаны строковые идентификаторы (стр. 44).
2.4. Тип данных свойства объекта - приведен в описании свойств объекта в спецификации BACnet. В
зависимости от типа данных свойства объекта выбирается тип сигнала и протокольный тип
Alpha.Server для получения значения или отправки команды. Для настройки адреса используется
соответствующий протокольный тип (стр. 46).
2.1. Пример устройства
Требуется получать от устройства значение температуры в помещении, а также задавать нижнее и верхнее
допустимые значения.
Информация об устройстве из объекта «Device»:
Свойство
Значение
Описание
«Object_Identifier»
«1»
Идентификатор устройства
Измеряемой температуре в устройстве соответствует объект «Analog_Input» со строковым
идентификатором «AI» (стр. 44) и номером экземпляра «0».
Свойства объекта «Analog_Input»:
Свойство
Идентификатор
Тип данных
Описание
«Object_Name»
77
CharacterString
Имя объекта
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
7

=== Page 440 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
Свойство
Идентификатор
Тип данных
Описание
«Present_Value»
85
REAL
Текущее значение температуры
«High_Limit»
45
REAL
Верхнее допустимое значение
«Low_Limit»
59
REAL
Нижнее допустимое значение
2.2. Настройка в Alpha.DevStudio
Чтобы настроить обмен данными с устройством по протоколу BACnet в Alpha.DevStudio:
добавьте в проект и настройте источник данных - устройство BACnet, с которым будет выполняться
обмен данными (стр. 8);
добавьте в Alpha.Server и настройте опросчик BACnet (стр. 14);
примените конфигурацию Alpha.Server (стр. 21).
ОБРАТИТЕ ВНИМАНИЕ
Порядок создания проекта и конфигурирование Alpha.Server описаны в документации на
Alpha.DevStudio (раздел «Знакомство с Alpha.DevStudio» руководства пользователя).
Далее приведено описание настройки обмена данными по протоколу BACnet уже
сконфигурированного Alpha.Server в существующем проекте.
2.2.1. Настройка источника данных
1. Перейдите в Alpha.Domain.
8
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 441 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
2. Добавьте в структуру домена элемент Компьютер и задайте имя, например, «BACnet Device».
Добавленный элемент представляет источник данных - устройство BACnet.
3. Перейдите в устройство «BACnet Device».
4. Элементу EthernetAdapter задайте значения свойств:
Сеть - выберите сеть домена;
Адрес - произвольный IP-адрес или адрес устройства BACnet.
ПРИМЕЧАНИЕ
В поле Адрес необходимо обязательно указать IP-адрес для того, чтобы проект
скомпилировался. Можно указать любой произвольный IP-адрес или IP-адрес устройства
BACnet, если он известен.
5. Добавьте элемент Исполняющий компонент, который будет выполнять роль устройства BACnet.
6. Перейдите в добавленный исполняющий компонент.
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
9

=== Page 442 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
7. Добавьте элемент Приложение.
8. Перейдите в добавленное приложение.
9. Добавьте элемент Логический объект и задайте ему имя, например, «Temperature».
10
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 443 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
10. Далее следует создать сигналы, значения которых будет получать и отправлять Alpha.Server. Для
этого в объект «Temperature» добавьте:
10.1. Сигналы, значения которых Alpha.Server будет получать от устройства BACnet (стр. 7):
Сигнал
Тип
Описание
«Name»
string
Имя объекта
«Temp»
float
Текущее значение температуры
«High_Limit»
float
Текущее верхнее допустимое значение
«Low_Limit»
float
Текущее нижнее допустимое значение
Для каждого сигнала задайте свойству Направление значение «выход».
10.2. Сигналы, значения которых Alpha.Server будет отправлять в устройство BACnet:
Сигнал
Тип
Описание
«Set_High_Limit»
float
Установка верхнего допустимого значения
«Set_Low_Limit»
float
Установка нижнего допустимого значения
Для каждого сигнала задайте свойству Направление значение «вход».
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
11

=== Page 444 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
11. Вернитесь в приложение и добавьте элемент Карта адресов BACnet.
12. Элементу Карта адресов BACnet создайте новый или укажите существующий файл карты адресов,
нажав кнопку
.
13. Перейдите в карту адресов «BACnetAddressMap». В ней отображаются все сигналы, ранее
добавленные в приложение.
14. Настройте параметры адресов сигналов:
Привязка - «непосредственно»;
Тип объекта - «AI» (объект «Analog_Input»);
Экземпляр объекта - «0» (номер экземпляра объекта типа «AI» в устройстве BACnet);
Значения параметров Свойство объекта и Протокольный тип укажите в соответствии с таблицей:
Сигнал
Свойство объекта
Протокольный тип
«Name»
OBJECT_NAME
CharacterString
«Temp»
PRESENT_VALUE
REAL
«High_Limit»
45
REAL
«Low_Limit»
59
REAL
«Set_High_Limit»
45
REAL
«Set_Low_Limit»
59
REAL
12
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 445 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
Заполненная карта адресов:
15. Вернитесь в исполняющий компонент и добавьте элемент Устройство BACnet.
16. Устройству BACnet задайте значения свойств (пример устройства) (стр. 7):
Карта адресов - укажите добавленную ранее карту адресов «BACnetAddressMap»;
Идентификатор устройства - идентификатор, указанный в объекте «Device» свойстве «Object_
Identifier» (в примере устройства идентификатор имеет значение «1»).
Значение свойства Номер UDP порта можно оставить по умолчанию, если не используется другой порт.
Значение свойства Имя можно оставить по умолчанию или указать другое, например, «DEV 1».
Свойства устройства BACnet:
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
13

=== Page 446 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
Свойство
Описание
Общие
Карта адресов
Расположение в проекте карты адресов с настройками сигналов.
Идентификатор
устройства
Идентификатор, указанный в настройках устройства, к которому выполняется
подключение (объект «Device», свойство «Object_Identifier»).
Номер UDP
порта
Порт для обмена данными с устройствами по протоколу BACnet. По умолчанию
используется порт «47808».
Имя
Название устройства, к которому выполняется подключение.
2.2.2. Настройка опросчика BACnet
1. Перейдите в Alpha.Domain.
2. Перейдите в узел домена «Server» и проверьте IP-адрес адаптера EthernetAdapter. IP-адрес адаптера
должен соответствовать IP-адресу компьютера, на котором функционирует Alpha.Server.
ПРИМЕЧАНИЕ
После компиляции IP-адрес в конфигурации модуля будет заменён на широковещательный
«0.0.0.0».
14
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 447 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
3. Перейдите в Alpha.Server и добавьте элемент Опросчик BACnet. Для свойств опросчика можно
оставить значения по умолчанию.
Свойства опросчика BACnet:
Свойство
Описание
Параметры модуля
Активность
Активность модуля при запуске/перезапуске Alpha.Server:
«Да» – модуль запущен;
«Нет» – модуль остановлен.
Управляется служебным сигналом «Active.Set».
Отображаемое
имя
Название модуля, которое отображается в тегах служебных сигналов.
Параметры журналирования
Вести журнал
работы модуля
Ведение записи сообщений о работе модуля в журнал работы:
«Да» – вести журнал работы;
«Нет» – журнал работы не ведётся.
Управляется служебным сигналом «FrameLogEnable.Set».
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
15

=== Page 448 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
Свойство
Описание
Размер журнала
работы модуля,
МБ
Размер файла журнала работы модуля в мегабайтах. При достижении
максимального размера создается новый файл, копия старого файла хранится на
рабочем диске.
Количество
дополнительных
журналов
работы
Количество файлов заполненных журналов работы модуля:
минимальное количество – 1;
максимальное количество – 255.
Уровень
трассировки в
журнал
приложений
Типы сообщений, которые выводятся в журнал приложений:
«Предупреждения и аварийные сообщения» – логические ошибки и ошибки
работы модуля. Предупреждения содержат некритичные ошибки. Аварийные
сообщения информируют об ошибках, которые влияют на работоспособность
сервера;
«Информационные сообщения» – предупреждения и аварийные сообщения, а
также основная информация о работе модуля;
«Отладочные сообщения» – предупреждения и аварийные сообщения,
основная и детальная информация о работе модуля.
Управляется служебным сигналом «SystemLogTraceLevel.Set».
Общие
Имя
Идентификатор модуля в конфигурации Alpha.Server, значение сервисного сигнала
«Id».
16
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 449 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
4. На элементе Опросчик BACnet нажмите кнопку
и укажите ранее сконфигурированное устройство
«DEV 1».
Чтобы перейти к настройкам параметров взаимодействия опросчика с устройством BACnet, выделите
добавленное устройство в Опросчике BACnet.
Для параметров взаимодействия опросчика с устройством можно оставить значения по умолчанию.
Свойство
Описание
Общие
Устройство
BACnet
Расположение в проекте Устройства BACnet.
Тайм-аут
операций с
устройством, мс
Промежуток времени, через который связь с устройством считается потерянной.
Отсчитывается с момента отправки последнего исходящего кадра. Значение по
умолчанию «1000» милисекунд.
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
17

=== Page 450 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
Свойство
Описание
Пауза между
циклами
поллинга, мс
Промежуток времени, через которой повторятся опрос устройства. Значение по
умолчанию «1000» милисекунд.
Период
обнаружения
устройства, мс
Промежуток времени, через который устройству отправляется запрос для
подтверждения наличия связи. Отсчитывается с момента отправки последнего
исходящего кадра Who-Is при обнаружении устройства, а также с момента
получения последнего входящего кадра при опросе устройства. Значение по
умолчанию «1500» милисекунд.
5. Если в конфигурации Alpha.Server отсутствует элемент Приложение, то добавьте его.
6. Перейдите в приложение и добавьте элемент Логический объект.
18
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 451 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
7. Перейдите в логический объект и добавьте элемент Объектная ссылка.
8. В свойстве Объект объектной ссылки укажите сконфигурированный ранее логический объект
«Temperature».
9. Экспонируйте входы и выходы, выполнив соответствующую команду контекстного меню объектной
ссылки.
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
19

=== Page 452 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
После выполнения команды в логическом объекте Alpha.Server отобразятся ранее
сконфигурированные сигналы устройства BACnet.
10. Добавьте сигналы доставки отправленных значений:
Сигнал
Тип
Описание
«Set_High_Limit_Delivery»
int1
Доставка команды установки верхнего допустимого
значения
«Set_Low_Limit_Delivery»
int1
Доставка команды установки нижнего допустимого
значения
20
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 453 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
11. Настройте сигналы доставки команд. Для этого соедините сигнал отправки значения с
соответствующим сигналом доставки, а в свойстве линии связи установите свойству Действие значение
«Статус доставки команды».
2.2.3. Применение конфигурации Alpha.Server
1. Постройте решение. Конфигурация Alpha.Server будет построена.
2. Перейдите в Мастер развёртывания.
ОБРАТИТЕ ВНИМАНИЕ
Для успешного применения построенных конфигураций должен быть настроен Alpha.Domain.
Описание настройки приведено в документации на Alpha.Domain (см. раздел
«Конфигурирование» руководства администратора).
3. Примените конфигурацию к Alpha.Server.
2.3. Настройка в Конфигураторе
Чтобы настроить обмен данными с устройством по протоколу BACnet:
добавьте в конфигурацию Alpha.Server и настройте модуль BACnet Client;
добавьте в конфигурацию Alpha.Server сигналы для получения и отправки значений
соответствующих типов;
настройте адреса сигналов;
перезапустите Alpha.Server.
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
21

=== Page 454 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
2.3.1. Настройка конфигурации модулей
В сервисном приложении Конфигуратор на вкладке Модули:
1. Заблокируйте ветку модулей конфигурации кнопкой
на панели инструментов.
2. Добавьте в состав конфигурации Alpha.Server модуль BACnet Client.
ОБРАТИТЕ ВНИМАНИЕ
Одновременно в составе конфигурации Alpha.Server может функционировать только один
экземпляр модуля BACnet Client.
22
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 455 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
3. В группе Общие установите параметрам Активность и Вести журнал работы модуля значения «Да»,
чтобы модуль запускался при запуске/перезапуске Alpha.Server и вёл журнал работы (стр. 42).
Значения остальных параметров группы Общие можно установить по желанию или оставить значения по
умолчанию.
Общие параметры работы модуля:
Параметр
Описание
Имя модуля
Название модуля, которое отображается в тегах служебных сигналов, а также в
дереве модулей и Редакторе адреса в Конфигураторе.
Идентификатор
модуля
Идентификатор модуля в конфигурации Alpha.Server, включаемый в параметры
адреса сигнала в Конфигураторе, а также значение сервисного сигнала «Id».
Активность
Активность модуля при запуске/перезапуске Alpha.Server:
«Да» – модуль запущен;
«Нет» – модуль остановлен.
Управляется служебным сигналом «Active.Set».
Уровень
трассировки в
журнал
приложений
Типы сообщений, которые выводятся в журнал приложений:
«Предупреждения и аварийные сообщения» – логические ошибки и ошибки
работы модуля. Предупреждения содержат некритичные ошибки. Аварийные
сообщения информируют об ошибках, которые влияют на работоспособность
сервера;
«Информационные сообщения» – предупреждения и аварийные сообщения, а
также основная информация о работе модуля;
«Отладочные сообщения» – предупреждения и аварийные сообщения,
основная и детальная информация о работе модуля.
Управляется служебным сигналом «SystemLogTraceLevel.Set».
Вести журнал
работы модуля
Ведение записи сообщений о работе модуля в журнал работы:
«Да» – вести журнал работы;
«Нет» – журнал работы не ведётся.
Управляется служебным сигналом «FrameLogEnable.Set».
Размер журнала
работы модуля,
МБ
Размер файла журнала работы модуля в мегабайтах. При достижении
максимального размера создается новый файл, копия старого файла хранится на
рабочем диске.
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
23

=== Page 456 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
Параметр
Описание
Количество
дополнительных
журналов работы
Количество файлов заполненных журналов работы модуля:
минимальное количество – 1;
максимальное количество – 255.
4. Чтобы добавить интерфейс:
4.1. Выберите узел дерева BACnet/IP и нажмите кнопку
.
4.2. В появившемся окне добавьте интерфейс:
5. Настройте параметр интерфейса Конечная точка - IP-адрес компьютера, на котором установлен
Alpha.Server. Для остальных параметров можно оставить значения по умолчанию.
Параметры интерфейса:
Параметр
Описание
Имя
интерфейса
Название интерфейса.
Номер
порта UDP
Порт для обмена данными с устройствами по протоколу BACnet. По умолчанию
используется порт «47808».
Конечная
точка
IP-адрес сетевого интерфейса компьютера, на котором установлен Alpha.Server. Если
компьютер имеет только один сетевой интерфейс или нужные устройства доступны по
всем интерфесам компьютера, то используется адрес «0.0.0.0».
24
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 457 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
6. Чтобы добавить устройство:
6.1. Выберите узел дерева Список устройств и нажмите кнопку
.
6.2. В появившемся окне добавьте устройство.
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
25

=== Page 458 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
7. Настройте параметры устройства (стр. 7):
Идентификатор устройства - «1» (объект «Device», свойство «Object_Identifier»).
Для остальных параметров можно оставить значения по умолчанию.
Параметры устройства:
Параметр
Описание
Имя устройства
Название устройства в конфигурации модуля.
Идентификатор
устройства
Идентификатор, указанный в настройках устройства, к которому выполняется
подключение (объект «Device», свойство «Object_Identifier»).
Тип устройства
Название типа устройства. Выбирается из списка доступных типов устройств в
конфигурации модуля, либо не указывается.
Тайм-аут
операций с
устройством, мс
Промежуток времени, через который связь с устройством считается потерянной.
Отсчитывается с момента отправки последнего исходящего кадра. Значение по
умолчанию «1000» милисекунд.
Пауза между
циклами
поллинга, мс
Промежуток времени, через которой повторятся опрос устройства. Значение по
умолчанию «1000» милисекунд.
Период
обнаружения
устройства, мс
Промежуток времени, через который устройству отправляется запрос для
подтверждения наличия связи. Отсчитывается с момента отправки последнего
исходящего кадра Who-Is при обнаружении устройства, а также с момента
получения последнего входящего кадра при опросе устройства. Значение по
умолчанию «1500» милисекунд.
8. Чтобы просматривать и изменять значения сигналов Alpha.Server через OPC клиент, добавьте в
состав конфигурации один из модулей:
OPC UA – если требуется просматривать и изменять значения сигналов по OPC UA;
OPC DA Server – если требуется просматривать и изменять значения сигналов по OPC DA
(только в ОС Windows).
В настройках добавленного модуля установите параметру Активность значение «Да».
9. Разблокируйте ветку модулей конфигурации кнопкой
на панели инструментов и сохраните
изменения.
10. Перезапустите Alpha.Server.
26
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 459 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
2.3.2. Настройка сигналов
2.3.2.1. Добавление сигналов
В сервисном приложении Конфигуратор на вкладке Сигналы добавьте сигналы для обмена данными с
устройством (стр. 7):
1. Сигналы, значения которых Alpha.Server будет получать от устройства BACnet:
Параметр
Тип
Назначение
«Name»
string
Имя объекта
«Temp»
float
Текущее значение температуры
«High_Limit»
float
Текущее верхнее допустимое значение
«Low_Limit»
float
Текущее нижнее допустимое значение
2. Сигналы, значения которых Alpha.Server будет отправлять в устройство BACnet:
Параметр
Тип
Назначение
«Set_High_Limit»
float
Установка верхнего допустимого значения
«Set_Low_Limit»
float
Установка нижнего допустимого значения
3. Сигналы доставки отправленных значений в устройство BACnet:
Параметр
Тип
Назначение
«Set_High_Limit_Delivery»
int1
Доставка команды установки верхнего допустимого значения
«Set_Low_Limit_Delivery»
int1
Доставка команды установки нижнего допустимого значения
Схема обмена данными:
2.3.2.2. Настройка адреса сигнала
Для обмена данными с устройством выполните настройку адреса для каждого сигнала:
1. Добавьте сигналу свойство 5000 (Address).
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
27

=== Page 460 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
2. В Редакторе адреса добавьте модуль BACnet Client.
3. Настройте параметры Редактора адреса:
В конфигурации Alpha.Server адрес сигнала представлен в виде строки со значениями параметров.
В таблице приведены параметры адреса сигнала для модуляBACnet Client, а также поля Редактора адреса
для настройки параметров.
Параметр
Редактор
адреса
Значение
ModuleId
–
Идентификатор модуля
Protocol
–
BACnet
Station
Устройство
Имя устройства (стр. 26)
28
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 461 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
Параметр
Редактор
адреса
Значение
Address
Адрес
Полный адрес свойства объекта. Формат адресной строки:
Object_Type:Object_Instance:Prop_Index[Array_Index]
где:
«Object_Type» - строковый идентификатор (стр. 44) или
идентификатор типа объекта;
«Object_Instance» - номер экземпляра объекта в устройстве;
«Prop_Index» - строковый идентификатор (стр. 44) или
идентификатор свойства объекта;
«Array_Index» - индекс в массиве данных свойств объекта
(необязательный параметр).
ПРИМЕР
Адрес, соответствующий свойству «Present_Value» (85) объекта
«Analog_Input» (AI или 0):
AI:0:PRESENT_VALUE
равнозначно:
0:0:85
ProtocolType
Протокольный
тип
Тип, значение которого выбирается в зависимости от направления сигнала
и типа данных свойства объекта в устройстве:
«IN_*» - входящий сигнал;
«OUT_*» - исходящий сигнал;
«INTERNAL_CTRLRES» - сигнал доставки;
где * - протокольнй тип в зависимости от типа данных свойства объекта
(стр. 46).
Получение значения свойства объекта
Чтобы настроить получение значений свойства объекта, в Редакторе адреса сигнала укажите (стр. 7):
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
29

=== Page 462 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
в поле Устройство - «DEV 1» (имя устройства, от которого требуется получать данные);
в полях Адрес и Протокольный тип - значения в соответствии с таблицей:
Сигнал
Адрес
Протокольный тип
«Name»
AI:0:77
IN_CharacterString
«Temp»
AI:0:85
IN_REAL
«High_Limit»
AI:0:45
IN_REAL
«Low_Limit»
AI:0:59
IN_REAL
Настроенные адреса сигналов:
1. Адрес сигнала «Name»:
Адрес сигнала «Name» в конфигурации сервера:
{ModuleId=(BACnet Client) Protocol=(BACnet) Station=(DEV 1) Address=(AI:0:77)
ProtocolType=(IN_CharacterString)}
2. Адрес сигнала «Temp»:
Адрес сигнала «Temp» в конфигурации сервера:
{ModuleId=(BACnet Client) Protocol=(BACnet) Station=(DEV 1) Address=(AI:0:85)
ProtocolType=(IN_REAL)}
30
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 463 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
3. Адрес сигнала «High_Limit»:
Адрес сигнала «High_Limit» в конфигурации сервера:
{ModuleId=(BACnet Client) Protocol=(BACnet) Station=(DEV 1) Address=(AI:0:45)
ProtocolType=(IN_REAL)}
4. Адрес сигнала «Low_Limit»:
Адрес сигнала «Low_Limit» в конфигурации сервера:
{ModuleId=(BACnet Client) Protocol=(BACnet) Station=(DEV 1) Address=(AI:0:59)
ProtocolType=(IN_REAL)}
Подача команды управления
Чтобы настроить подачу команды управления устройству, в Редакторе адреса сигнала укажите:
в поле Устройство - «DEV 1» (имя устройства, которому требуется подавать команду);
в полях Адрес и Протокольный тип - значения в соответствии с таблицей:
Сигнал
Свойство объекта
Протокольный тип
«Set_High_Limit»
AI:0:45
OUT_REAL
«Set_Low_Limit»
AI:0:59
OUT_REAL
Настроенные адреса сигналов:
1. Адрес сигнала «Set_High_Limit»:
Адрес сигнала «Set_High_Limit» в конфигурации сервера:
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
31

=== Page 464 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
{ModuleId=(BACnet Client) Protocol=(BACnet) Station=(DEV 1) Address=(AI:0:45)
ProtocolType=(OUT_REAL)}
2. Адрес сигнала «Set_Low_Limit»:
Адрес сигнала «Set_Low_Limit» в конфигурации сервера:
{ModuleId=(BACnet Client) Protocol=(BACnet) Station=(DEV 1) Address=(AI:0:59)
ProtocolType=(OUT_REAL)}
Настройка сигнала доставки
Чтобы настроить сигнал доставки команды управления, в Редакторе адреса:
укажите значения параметров Устройство и Адрес, равными значениям этих же параметров сигнала
команды управления;
параметру Протокольный тип установите значение INTERNAL_CTRLRES.
Сигнал
Свойство объекта
Протокольный тип
«Set_High_Limit_Delivery»
AI:0:45
INTERNAL_CTRLRES
«Set_Low_Limit_Delivery»
AI:0:59
INTERNAL_CTRLRES
Настроенные адреса сигналов:
1. Адрес сигнала «Set_High_Limit_Delivery»:
Адрес сигнала «Set_High_Limit_Delivery» в конфигурации сервера:
{ModuleId=(BACnet Client) Protocol=(BACnet) Station=(DEV 1) Address=(AI:0:45)
ProtocolType=(INTERNAL_CTRLRES)}
32
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 465 ===
2. НАСТРОЙКА ОБМЕНА ДАННЫМИ С УСТРОЙСТВОМ
2. Адрес сигнала «Set_Low_Limit_Delivery»:
Адрес сигнала «Set_Low_Limit_Delivery» в конфигурации сервера:
{ModuleId=(BACnet Client) Protocol=(BACnet) Station=(DEV 1) Address=(AI:0:59)
ProtocolType=(INTERNAL_CTRLRES)}
ОБРАТИТЕ ВНИМАНИЕ
После настройки адресов сигналов перезапустите Alpha.Server.
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
33

=== Page 466 ===
3. ПРОВЕРКА ОБМЕНА ДАННЫМИ
3. Проверка обмена данными
Чтобы проверить выполнение обмена данными между модулем BACnet Client и устройством BACnet:
1. Подключитесь к Alpha.Server с помощью OPC клиента, например, OpcExplorer.
2. В Инспектор добавьте сигналы «Name», «Temp», «High_Limit» и «Low_Limit».
3. На стороне устройства установите соответствующим свойствам некоторые значения, например:
«Object_Name»: «Помещение №3»;
«Present_Value»: «25»;
«High_Limit»: «30»;
«Low_Limit»: «20».
4. Проконтролируйте соответствующие изменения значений сигналов в OpcExplorer.
5. В Инспектор добавьте сигналы «Set_High_Limit», «Set_Low_Limit», «Set_High_Limit_Delivery» и
«Set_Low_Limit_Delivery».
6. В OpcExplorer установите сигналам некоторые значения, например:
«Set_High_Limit»: «40»;
«Set_Low_Limit»: «15».
7. Проконтролируйте полученные значения сигналов доставки «Set_High_Limit_Delivery» и «Set_Low_
Limit_Delivery» (стр. 48), а также новые значения сигналов «High_Limit» и «Low_Limit».
8. На стороне устройства проконтролируйте изменение значений свойств «High_Limit» и «Low_Limit».
Проконтролировать работу модуля можно в сервисном приложении Просмотрщик лога кадров, открыв
журнал работы модуля (стр. 42).
34
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 467 ===
4. ДИАГНОСТИКА РАБОТЫ
4. Диагностика работы
4.1. Служебные сигналы
Модуль BACnet Client динамически создаёт служебные сигналы:
контроля и управления подключаемыми источниками;
управления подпиской на свойства объектов;
контроля и управления основными параметрами модуля.
4.1.1. Контроль и управление подключаемым источником
Полный тег служебного сигнала контроля состояния соединения с подключаемым устройством имеет вид:
Service.Modules.<Имя модуля>.<Имя источника>.<Имя устройства>.IsConnected
Полный тег служебных сигналов управления подключаемым источником имеет вид:
Service.Modules.<Имя модуля>.<Имя источника>.<Имя сигнала>
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
35

=== Page 468 ===
4. ДИАГНОСТИКА РАБОТЫ
Сигнал
Тип
Описание сигнала
«IsConnected»
Bool
Состояние соединения с устройством:
«True» – связь установлена;
«False» – связь отсутствует.
«GetData»
Bool
Команда запроса всех данных по источнику:
«True» – запросить данные источника.
«SynchronizeAllEventStates»
Bool
Команда синхронизации событий с источником:
«True» – синхронизировать события с
источником.
4.1.2. Управление подпиской на свойства объектов
Полный тег служебного сигнала типа String управления подпиской на свойства объектов имеет вид:
Service.Modules.<Имя модуля>.SetSubscription
36
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 469 ===
4. ДИАГНОСТИКА РАБОТЫ
Для подписки на свойство объекта в значение сигнала «SetSubscription» следует записать JSON-строку в
формате:
{"subscribe":{"SubscriptionID": "<value>","Priority": <value>, "Filter":{"DataCategories":
"<value>"],"Tags": ["<value>"],"Area": "<value>"},"Settings":{"Lifetime":<value>}}}
Для отписки от свойства объекта в значение сигнала «SetSubscription» следует записать JSON-строку в
формате:
{"unsubscribe":{"SubscriptionID": "<value>"}}
Обязательный атрибут JSON-строки:
SubscriptionID - Идентификатор подписки, заданный произвольно. Используется для
идентификации процесса, выполняющего подписку или отписку. Для выполнения подписки и отписки на
одни и те же данные SubscriptionID для подписки и отписки должен совпадать.
Необязательные атрибуты JSON-строки:
Filter - Информация о сигналах, для которых необходимо применить подписку. Если данное поле не
указано, то операция будет выполнена для сигналов, связанных через служебную связь:
Если сигнал определён для определенного свойства, то операция не требует Filter и при его
указании не будет выполнена.
Если сигнал определён для объекта, то операция выполняется для всех свойств объекта.
Для Filter можно указывать дополнительные параметры. Фильтрация возможна по одному из
параметров:
DataCategories - массив строк с указанием одного или нескольких имён категорий данных.
Tags - массив строк с указанием одного или нескольких полных тегов сигналов. Полные теги
могут быть указаны для сигналов на уровне:
ПЛК, для которых указаны карты адресов;
Alpha.Server, в которые выполняется прямая перекладка.
Area - указание узла дерева, для дочерних узлов которого будет выполнена подписка. Указание
Area доступно только при изменении состояния подписки для модуля.
Priority - разделение подписок по приоритетам. Задаётся от «0» до «255», где «0» - самый высокий
приоритет. Если приоритет не задан, то приоритет считается равным «0».
С помощью приоритета можно разделять подписки по важности. Максимальное количество подписок
указывается в параметрах подписки устройства.
Lifetime - время жизни подписки в секундах. Если врмя жизни подписки не задано, то используется
значение, указанное в параметрах источника.
4.1.3. Контроль и управление основными параметрами модуля
Полный тег стандартных служебных сигналов имеет вид:
Service.Modules.<Имя модуля>.<Имя сигнала>
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
37

=== Page 470 ===
4. ДИАГНОСТИКА РАБОТЫ
Сигнал
Тип
Описание сигнала
«Active»
Bool
Активность модуля:
«True» – запущен;
«False» – остановлен.
Соответствует значению параметра Активность. Управляется
служебным сигналом «Active.Set»
«FrameLogEnable»
Bool
Ведение журнала работы:
«True» – ведется;
«False» – не ведётся.
Соответствует значению параметра Вести журнал работы модуля.
Управляется служебным сигналом «FrameLogEnable.Set»
«SystemLogTraceLevel»
Uint4
Уровень детализации журнала работы:
«1» – Предупреждения и аварийные сообщения;
«2» – Информационные сообщения;
«3» – Отладочные сообщения.
Соответствует значению параметра Уровень трассировки в журнал
приложений. Управляется служебным сигналом
«SystemLogTraceLevel.Set»
«Id»
String
Идентификатор модуля в конфигурации Alpha.Server
4.2. Параметры статистики
Статистическая информация о работе Alpha.Server отображается на вкладке Статистика сервисного
приложения Конфигуратор, а также в сервисном приложении Статистика. Чтобы просмотреть
статистическую информацию модуля BACnet Client, запустите сервисное приложение Статистика или
Конфигуратор, и подключитесь к Alpha.Server.
4.2.1. Статистика модуля
Чтобы посмотреть статистику работы модуля, выделите в дереве статистики узел модуля BACnet Client.
38
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 471 ===
4. ДИАГНОСТИКА РАБОТЫ
Параметр
Описание
Общие параметры:
Идентификатор модуля
Идентификатор модуля в конфигурации Alpha.Server.
Имя модуля
Название модуля.
Исполняемый файл
Имя исполняемого файла модуля в каталоге установки
Alpha.Server.
Версия
Версия модуля BACnet Client.
Активность
Активность модуля.
Вести журнал работы модуля
Ведение записи сообщений о работе модуля в журнал работы.
Уровень детализации журнала
работы
Типы сообщений, которые фиксируются в журнал приложений.
Предельный размер лога кадров
Размер файла в мегабайтах для записи журнала работы модуля.
Время старта
Время запуска модуля.
Лицензия
Текущее состояние лицензирования модуля.
4.2.2. Статистика источника
Чтобы посмотреть статистику источника, выделите в дереве статистики узел соответствующего источника.
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
39

=== Page 472 ===
4. ДИАГНОСТИКА РАБОТЫ
Параметр
Описание
Количество источников событий
Общее количество сигналов, принятых на обслуживание в
качестве источников событий.
Количество исходящих сигналов
Общее количество исходящих сигналов, принятых на
обслуживание.
Входящие сигналы
Количество сигналов по запросу
Общее количество входящих сигналов, получаемых по
запросу.
Количество сигналов по опросу
Общее количество входящих сигналов, получаемых по
опросу.
Количество сигналов по подписке с
подтверждением
Общее количество входящих сигналов, получаемых по
подписке с подтверждением.
Количество сигналов по подписке без
подтверждения
Общее количество входящих сигналов, получаемых по
подписке без подтверждения.
Количество сигналов по подписке на
объект с подтверждением
Общее количество входящих сигналов, получаемых по
подписке на объект с подтверждением.
Количество сигналов по подписке на
объект без подтверждения
Общее количество входящих сигналов, получаемых по
подписке на объект без подтверждения.
Активные COV подписки
Количество статических COV подписок
Общее количество статических COV подписок.
Количество динамических COV подписок
Общее количество динамических COV подписок.
Количество клиентских подписок
Общее количество клиентских подписок.
4.2.3. Статистика устройства
Чтобы посмотреть статистику устройства, выделите в дереве статистики узел соответствующего устройства.
Параметр
Описание
Состояние
Текущее состояние устройства с указанием времени последнего
изменения.
40
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 473 ===
4. ДИАГНОСТИКА РАБОТЫ
Параметр
Описание
Соединение
Текущее состояние соединения с устройством с указанием времени
последнего изменения.
Принято событий
Общее количество принятых событий.
Принято COV уведомлений
Общее количество принятых COV уведомлений.
Успешно отправленных значений в
устройство
Общее количество успешно отправленных значений в устройство.
4.2.4. Статистика канала
Чтобы посмотреть статистику канала, выделите в дереве статистики узел соответствующего канала
устройства.
Параметр
Описание
Информация о соединении
Конечная точка
IP адрес и порт канала.
NET
Сеть BACnet.
MAC
MAC адрес.
4.2.5. Статистика локальных интерфейсов
Чтобы посмотреть статистику локальных интерфейсов, выделите в дереве статистики узел
соответствующего интерфейса.
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
41

=== Page 474 ===
4. ДИАГНОСТИКА РАБОТЫ
Параметр
Описание
Отправлено байт
Количество байт, отправленных по интерфейсу.
Принято байт
Количество байт, полученных по интерфейсу.
4.3. Журнал работы
Модуль BACnet Client ведёт журнал работы, в который записывается информация об обмене данными с
устройствами и работе модуля.
ОБРАТИТЕ ВНИМАНИЕ
Чтобы модуль вёл журнал работы, в общих параметрах модуля в Конфигураторе или в свойствах
опросчика в Alpha.DevStudio установите параметру Вести журнал работы модуля значение «Да» или
установите сервисному сигналу модуля «FrameLogEnable.Set» значение «true».
Журнал работы модуля сохраняется в файл <имя модуля>.aplog по умолчанию:
в папке C:\Program Files\Automiq\Alpha.Server\Logs, если Alpha.Server функционирует в ОС
Windows;
в директории /opt/Automiq/Alpha.Server/Logs, если Alpha.Server функционирует в ОС семейства
Linux.
Для просмотра журнала работы модуля используется сервисное приложение Просмотрщик лога кадров.
Каждая запись журнала имеет порядковый номер, дату, время и описание. Записи исходящих и входящих
кадров дополнительно содержат IP-адреса отправителя и получателя.
Побайтовое представление и данные кадров модуля отображаются в соответствующих полях окна
сервисного приложения Просмотрщик лога кадров.
42
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 475 ===
4. ДИАГНОСТИКА РАБОТЫ
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
43

=== Page 476 ===
5. ПРИЛОЖЕНИЯ
5. Приложения
Приложение A: Строковые идентификаторы объектов и
свойств
В приложении приведены строковые идентификаторы типов объектов и свойств, поддерживаемые модулем
BACnet Client.
Типы объектов
Тип объекта в
спецификации BACnet
Идентификатор объекта в
спецификации BACnet
Строковый идентификатор объекта
в Alpha.Server
«Analog_Input»
0
AI
«Analog_Output»
1
AO
«Analog_Value»
2
AV
«Binary_Input»
3
BI
«Binary_Output»
4
BO
«Binary_Value»
5
BV
«Device»
8
DEVICE
Свойства объекта
Свойство объекта в
спецификации BACnet
Идентификатор свойства объекта в
спецификации BACnet
Строковый идентификатор
свойства в Alpha.Server
«APDU_Timeout»
11
APDU_TIMEOUT
«Application_Software_
Version»
12
APPLICATION_SOFTWARE_
VERSION
«Database_Revision»
155
DATABASE_REVISION
«Description»
28
DESCRIPTION
«Device_Address_Binding»
30
DEVICE_ADDRESS_BINDING
«Event_State»
36
EVENT_STATE
«Firmware_Revision»
44
FIRMWARE_REVISION
«Location»
58
LOCATION
44
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 477 ===
5. ПРИЛОЖЕНИЯ
Свойство объекта в
спецификации BACnet
Идентификатор свойства объекта в
спецификации BACnet
Строковый идентификатор
свойства в Alpha.Server
«Max_APDU_Length_
Accepted»
62
MAX_APDU_LENGTH_
ACCEPTED
«Model_Name»
70
MODEL_NAME
«Number_Of_APDU_Retries»
73
NUMBER_OF_APDU_RETRIES
«Object_Identifier»
75
OBJECT_IDENTIFIER
«Object_List»
76
OBJECT_LIST
«Object_Name»
77
OBJECT_NAME
«Object_Type»
79
OBJECT_TYPE
«Out_Of_Service»
81
OUT_OF_SERVICE
«Polarity»
84
POLARITY
«Present_Value»
85
PRESENT_VALUE
«Priority_Array»
87
PRIORITY_ARRAY
«Protocol_Object_Types_
Supported»
96
PROTOCOL_OBJECT_TYPES_
SUPPORTED
«Protocol_Revision»
139
PROTOCOL_REVISION
«Protocol_Services_
Supported»
97
PROTOCOL_SERVICES_
SUPPORTED
«Protocol_Version»
98
PROTOCOL_VERSION
«Reliability»
103
RELIABILITY
«Relinquish_Default»
104
RELINQUISH_DEFAULT
«Segmentation_Supported»
107
SEGMENTATION_SUPPORTED
«State_Text»
110
STATE_TEXT
«Status_Flags»
111
STATUS_FLAGS
«System_Status»
112
SYSTEM_STATUS
«Units»
117
UNITS
«Vendor_Identifier»
120
VENDOR_IDENTIFIER
«Vendor_Name»
121
VENDOR_NAME
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
45

=== Page 478 ===
5. ПРИЛОЖЕНИЯ
Приложение B: Протокольные типы
В таблицах приведены типы свойств объектов в спецификации BACnet, соответствующие им типы сигналов в
Alpha.Server и протокольные типы для настройки адресов сигналов Alpha.Server:
входящих сигналов - для получения значений свойств объектов устройства BACnet;
исходящих сигналов - для отправки команд управления в устройство BACnet.
Входящие сигналы
Тип свойства,
значение которого
требуется получить от
устройства
Тип сигнала в
Alpha.Server
Протокольный тип
Описание
BOOLEAN
bool
BOOLEAN
Логическое значение (true; false)
INTEGER
INTEGER16
int4
Signed
Целое знаковое 4 байта (от -2 147 483
648 до 2 147 483 647)
Unsigned
Unsigned8
Unsigned16
Unsigned32
uint4
Unsigned
Целое беззнаковое 4 байта (от 0 до 4
294 967 295)
ENUMERATED
uint4
Enum
Численные перечисления (стр. 49)
string
EnumStr
Строковые перечисления (стр. 49)
REAL
float
REAL
Вещественное 4 байта ([±1.5×10-45;
±3.4×1038]. Точность 6-9 цифр)
Double
double
double
Вещественное 8 байт ([±5.0×10-324;
±1.7×10308]. Точность 15-17 цифр)
CharacterString
string
CharacterString
Текстовая строка
OCTET STRING
string
OctetString
Массив байтов в виде строки
BIT STRING
string
BitString
Массив битов в виде строки
BACnetObjectIdentifier
string
ObjectIdStr
Идентификатор объекта в формате
<object_type>:<instance_num>
где:
object_type - идентификатор
типа объекта;
instance_num - номер
экземпляра объекта.
46
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 479 ===
5. ПРИЛОЖЕНИЯ
Тип свойства,
значение которого
требуется получить от
устройства
Тип сигнала в
Alpha.Server
Протокольный тип
Описание
Time
string
TimeStr
Время в формате
HH:MM:SS.ss
где:
HH - часы;
MM - минуты;
SS - секунды;
ss - милисекунды.
Date
string
DateStr
Дата в формате
YYYY:MM:DD
где:
YYYY - год;
MM - месяц;
DD - день.
Исходящие сигналы
Тип свойства, значение
которого требуется
изменить
Тип сигнала в
Alpha.Server
Протокольный
тип Alpha.Server
Описание
BOOLEAN
bool
BOOLEAN
Логическое значение (0, 1)
INTEGER
INTEGER16
int4
Signed
Целое знаковое 4 байта (от -2 147 483
648 до 2 147 483 647)
Unsigned
Unsigned8
Unsigned16
Unsigned32
uint4
Unsigned
Целое беззнаковое 4 байта (от 0 до 4
294 967 295)
ENUMERATED
uint4
Enum
Перечисления (от 0 до 4 294 967 295)
(стр. 49)
REAL
float
REAL
Вещественное 4 байта ([±1.5×10-45;
±3.4×1038]. Точность 6-9 цифр)
Double
double
double
Вещественное 8 байт ([±5.0×10-324;
±1.7×10308]. Точность 15-17 цифр)
CharacterString
string
CharacterString
Текстовая строка
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
47

=== Page 480 ===
5. ПРИЛОЖЕНИЯ
Приложение C: Значения сигнала доставки
Значение сигнала доставки определяет состояние отправленной команды. Возможные значения сигнала
доставки приведены в таблице:
Значение
Состояние команды управления
«1»
Команда успешно помещена в очередь на отправку
«3»
Команда исполнена
«-1»
Команда не исполнена (плохое качество, неверный формат данных, несоответствующий
режим работы модуля)
«-2»
Нет связи с устройством
«-3»
Переполнена очередь данных на отправку
«-4»
Протокольная ошибка подачи команды управления
«-5»
Внутренняя ошибка модуля
48
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 481 ===
5. ПРИЛОЖЕНИЯ
Приложение D: Настройка типа устройства в
Конфигураторе
Значения свойств объектов с типом ENUMERATED передаются в виде числового значения.
ПРИМЕР
Добавьте в конфигурацию сигналы для получения значения свойства «Object_Type» - числового и
строкового, и настройте их адреса:
«Object_Type_num» типа uint4
«Object_Type_Str» типа string
Проконтролируйте полученные значения сигналов в OpcExplorer. Строковое значение передаётся в
формате:
<Статусное сообщение модуля>:<Идентификатор свойства>:<Значение свойства>
Чтобы числовое значение преобразовывалось в строковое значение, более удобное для восприятия, в
Конфигураторе настройте тип устройства с перечнем соответствий числовых значений перечислений
строковым.
Чтобы добавить тип устройства:
1. Выберите узел дерева Типы устройств и нажмите кнопку
.
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
49

=== Page 482 ===
5. ПРИЛОЖЕНИЯ
2. В появившемся окне добавьте тип устройства.
Удаление устройств выполняется в этом же окне.
Импорт типа устройства из файла
Чтобы для добавляемого типа устройства импортировать данные из файла:
1. В окне Импорт данных типа устройства нажмите кнопку Да.
2. Выберите для импорта файл формата *.xml с описанием типа устройства.
Пример содержимого файла с описанием устройства:
<BACnetDeviceType TypeName="ControllerType">
<Enums>
<EnumCat UintValue="79" StrValue='OBJECT TYPE'>
<Enum UintValue="0" StrValue="ANALOG INPUT"/>
<Enum UintValue="1" StrValue="ANALOG OUTPUT"/>
<Enum UintValue="2" StrValue="ANALOG VALUE"/>
<Enum UintValue="3" StrValue="BINARY INPUT"/>
<Enum UintValue="4" StrValue="BINARY OUTPUT"/>
<Enum UintValue="5" StrValue="BINARY VALUE"/>
<Enum UintValue="8" StrValue="DEVICE"/>
</EnumCat>
</Enums>
</BACnetDeviceType>
50
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 483 ===
5. ПРИЛОЖЕНИЯ
3. После импорта в конфигурацию будет добавлен тип устройства, содержащий категории перечислений,
описанные в импортируемом файле.
Ручная настройка типа устройства
Чтобы настроить тип устройства вручную:
1. В окне Импорт данных типа устройства нажмите кнопку Нет.
2. Для добавленного типа устройства укажите название.
3. Чтобы добавить категорию перечислений, выберите узел дерева Категории перечислений и нажмите
кнопку
.
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
51

=== Page 484 ===
5. ПРИЛОЖЕНИЯ
4. Добавьте требуемое количество категорий перечислений.
5. Для каждой категории укажите Числовое значение, Строковое значение и добавьте Перечисления:
6. Для каждого перечисления укажите Числовое значение и Строковое значение.
7. Перейдите в параметры устройства и укажите для параметра Тип устройства добавленный тип с
перечислениями:
8. Перезапустите Alpha.Server.
52
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 485 ===
5. ПРИЛОЖЕНИЯ
ПРИМЕР
После настройки типа устройства значение сигнала «Object_Type_Str» отображается в строковом
виде.
ALPHA.SERVER. МОДУЛЬ BACNET CLIENT. РУКОВОДСТВО АДМИНИСТРАТОРА
53

=== Page 486 ===
Программный комплекс Альфа платформа
Alpha.Server 6.4
Модуль Data Buffer
Руководство администратора
Редакция
Соответствует версии ПО
7. Предварительная
6.4.28

=== Page 487 ===
© АО «Атомик Софт», 2015-2026. Все права защищены.
Авторские права на данный документ принадлежат АО «Атомик
Софт». Копирование, перепечатка и публикация любой части или
всего документа не допускается без письменного разрешения
правообладателя.

=== Page 488 ===
Содержание
1. Назначение и принципы работы
4
1.1. Принцип работы
4
1.1.1. Разбор идентифицирующего сигнала
5
2. Настройка
7
2.1. Добавление и настройка модуля
7
2.2. Настройка папки буфера
8
2.3. Настройка объектов-получателей данных
9
3. Пример настройки
12
4. Диагностика работы модуля
18
4.1. Статистика
18
4.2. Журнал работы модуля
18
Список терминов и сокращений
20
ALPHA.SERVER. МОДУЛЬ DATA BUFFER. РУКОВОДСТВО АДМИНИСТРАТОРА
3

=== Page 489 ===
1. НАЗНАЧЕНИЕ И ПРИНЦИПЫРАБОТЫ
1. Назначение и принципы работы
Alpha.Server получает от источников данные об объектах1. Для этого в Alpha.Server создаётся описание
соответствующих объектов: каждому параметру объекта соответствует отдельный сигнал, для которого
настраивается получение значений данного параметра объекта от соответствующего источника.
Однако, если в источнике выполняется буферизация отправляемых данных, то при получении данных из
буфера источника необходимо сначала определить объект, к которому относятся полученные данные, после
чего положить полученные данные в сигналы объекта-получателя.
Для решения данной задачи предназначен модуль Data Buffer.
Модуль Data Buffer выполняет следующие функции:
определяет объект-получатель данных в Alpha.Server
перекладывает полученные данные в сигналы объекта-получателя
1.1. Принцип работы
Буфер данных представляет из себя последовательность строк. Строка буфера данных – это отдельная
запись в буфере данных источника о некотором событии.
Строка буфера данных состоит из полей:
в одном из полей хранится код события и код объекта, в котором произошло событие. Данное поле
будем называть идентифицирующим;
1Под объектами здесь понимаются отдельные параметры или структуры, содержащие набор параметров
4
ALPHA.SERVER. МОДУЛЬ DATA BUFFER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 490 ===
1. НАЗНАЧЕНИЕ И ПРИНЦИПЫРАБОТЫ
В зависимости от реализации источника, код события может состоять из различного количества бит или
отсутствовать вовсе. В зависимости от устройства идентифицирующего поля в источнике, настраиваются
маски кода объекта и кода события в настройках модуля Data Buffer (см. подробнее).
в остальных полях хранятся параметры события.
ПРИМЕР
Примером параметра события является значение, вызвавшее событие.
Список полей в строке буфера одинаков для всех строк буфера данных и определяется устройством
источника.
В Alpha.Server получение данных из буфера источника может выполнять любой коммуникационный
модуль. Для того, чтобы получение данных из буфера источника и разбор полученных данных выполнялись
независимо, в Alpha.Server полученные данные записываются в специальную папку буфера:
каждое поле строки буфера записывается в подготовленный для него сигнал в папке буфера;
каждой строке буфера (их количество определяется настройками источника) в папке буфера
соответствует свой набор сигналов для хранения полей этой строки.
При записи строки буфера в сигналы значение идентифицирующего поля записывается последним:
изменение этого сигнала означает, что все поля строки буфера записаны в соответствующие им дочерние
сигналы и можно начинать разбор данных записанных в сигналы.
Разбор начинается при изменении значения идентифицирующего сигнала и состоит из следующих этапов:
получение кода объекта из идентифицирующего сигнала с помощью маски кода объекта;
перекладка значений сигналов из папки буфера в сигналы объекта, имеющего соответствующий код.
1.1.1. Разбор идентифицирующего сигнала
Ниже показано, как модуль выделяет из идентифицирующего сигнала код объекта и код события.
ALPHA.SERVER. МОДУЛЬ DATA BUFFER. РУКОВОДСТВО АДМИНИСТРАТОРА
5

=== Page 491 ===
1. НАЗНАЧЕНИЕ И ПРИНЦИПЫРАБОТЫ
В идентифицирующем сигнале (сигнал типа Uint4 в папке буфера) содержится значение (к примеру «555»).
Модуль Data Buffer работает с этим значением в шестнадцатеричной системе счисления.
Модуль производит разбор сигнала в соответствии с принципом наложения масок на значение сигнала по
правилам логической операции "И":
Маска значения – выделяет из сигнала часть, содержащую код события;
Маска кода объекта – выделяет из сигнала часть, содержащую код объекта.
Маски устанавливаются пользователем в настройках модуля.
ПРИМЕР
Выделение кода объекта
Выделение кода события
Результат разбора:
Код объекта – «2»
Код события – «2B» (в десятичной системе счисления – «43»)
После разбора буфера модуль запишет код события 43 в сигнал-получатель в объекте 2.
6
ALPHA.SERVER. МОДУЛЬ DATA BUFFER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 492 ===
2. НАСТРОЙКА
2. Настройка
Чтобы настроить работу модуля с данными, полученными из буфера источника, необходимо:
добавить модуль Data Buffer в конфигурацию Alpha.Server и настроить его;
настроить папку буфера;
настроить объекты-получатели данных.
2.1. Добавление и настройка модуля
Чтобы добавить модуль в состав конфигурации Alpha.Server, воспользуйтесь сервисным приложением
Конфигуратор.
После добавления модуля настройте его параметры.
Модуль Data Buffer имеет общие и дополнительные параметры.
Параметр
Описание
Имя модуля
Название модуля
Идентификатор
модуля
Идентификатор модуля
Активность
Активность модуля:
«Да» – модуль запущен
«Нет» – модуль остановлен
Общие параметры
ALPHA.SERVER. МОДУЛЬ DATA BUFFER. РУКОВОДСТВО АДМИНИСТРАТОРА
7

=== Page 493 ===
2. НАСТРОЙКА
Параметр
Описание
Уровень
трассировки в
журнал
приложений
Типы сообщений, которые фиксируются в журнал приложений:
«Предупреждения и аварийные сообщения» – логические ошибки, ошибки работы
модуля. Предупреждения содержат некритичные ошибки. Аварийные сообщения
информируют об ошибках, которые влияют на работоспособность службы
«Информационные сообщения» – сообщения, которые показывают основную
информацию о работе модуля
«Отладочные сообщения» – сообщения, которые наиболее детально отражают
информацию о работе модуля
Вышестоящий уровень входит в состав нижестоящего: если выбрано «Информационные
сообщения», то в журнал фиксируются «Предупреждения и аварийные сообщения» и
«Информационные сообщения»
Вести журнал
работы модуля
Ведётся ли журнал работы модуля:
«Да»
«Нет»
Размер журнала
работы модуля,
МБ
Ограничение на размер файла журнала работы модуля в мегабайтах.
При достижении максимального размера создается новый файл, копия старого файла
хранится на рабочем диске
Количество
дополнительных
журналов
работы
Количество файлов заполненных журналов работы модуля.
Минимальное значение – 1, максимальное – 255
Дополнительные параметры:
Параметр
Описание
Папка буфера
Папка, в дереве сигналов, используемая для получения данных из буфера
источника
Маска значения
Используется для выделения из идентифицирующего сигнала кода события
Маска кода объекта
Используется для выделения из идентифицирующего сигнала кода объекта
Режим изменения метки
времени при хорошем
качестве
«True» – модуль будет устанавливать значения целевых сигналов
только на основании изменений метки времени при хорошем качестве
сигнала-источника
«False» – модуль будет устанавливать значения целевых сигналов
при любых изменениях сигнала-источника
2.2. Настройка папки буфера
В дереве сигналов:
8
ALPHA.SERVER. МОДУЛЬ DATA BUFFER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 494 ===
2. НАСТРОЙКА
1. Создайте папку буфера.
2. В папке буфера создайте структуру сигналов, показанную на рисунке ниже.
ОБРАТИТЕ ВНИМАНИЕ
Названия на рисунке не являются названиями сигналов: они показывают соответствие сигналов и
"ячеек" в таблице буфера источника.
Примечания:
количество элементов в буфере N – определяется настройками источника;
тип идентифицирующих сигналов (отмечены на рисунке красным) – Uint4;
возможные типы сигналов-параметров (отмечены на рисунке зелёным): Int2, Uint2, Int4, Uint4, Float;
названия сигналов-параметров, соответствующих одному параметру в буфере должны быть
одинаковыми (сигналы «Elem1_Param1», «Elem2_Param1» и «ElemN_Param1», изображённые на рисунке,
должны иметь одно и то же название);
для каждого сигнала в свойстве 5000 (Address) выберите коммуникационный модуль,
принимающий данные из буфера источника, и укажите в его параметрах адрес в адресном пространстве
источника, из которого необходимо получать значение этого сигнала;
после подготовки одного набора сигналов (идентифицирующего сигнала и всех его дочерних
сигналов), остальные наборы сигналов можно создать с помощью размножения (выполняется в
контекстном меню идентифицирующего сигнала). В этом случае в сигналах, созданных размножением,
необходимо настроить свойство 5000 (Address).
2.3. Настройка объектов-получателей данных
В дереве сигналов:
1. Создайте папку объекта-получателя.
ALPHA.SERVER. МОДУЛЬ DATA BUFFER. РУКОВОДСТВО АДМИНИСТРАТОРА
9

=== Page 495 ===
2. НАСТРОЙКА
2. Созданной папке добавьте свойства:
999000 (ObjectType) – значение не указывается;
999001 (ObjectCode) – в качестве значения укажите код объекта.
3. В папке объекта-получателя создайте сигнал типа Uint4 – приёмник кода события.
4. Поставьте созданный сигнал на обслуживание модулю Data Buffer (выполняется в свойстве 5000
(Address)).
10
ALPHA.SERVER. МОДУЛЬ DATA BUFFER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 496 ===
2. НАСТРОЙКА
5. Для каждого параметра события:
создайте в объектной папке сигнал соответствующего типа;
поставьте созданный сигнал на обслуживание модулю Data Buffer с параметром «MemberId=
(<название параметра>)» (выполняется в свойстве 5000 (Address)).
ПРИМЕЧАНИЕ
Сигнал-приёмник кода события и сигналы-приёмники значений параметров могут находиться как
в корне объектной папки, так и в любой папке, находящейся в объектной папке (любого уровня
вложенности).
ALPHA.SERVER. МОДУЛЬ DATA BUFFER. РУКОВОДСТВО АДМИНИСТРАТОРА
11

=== Page 497 ===
3. ПРИМЕР НАСТРОЙКИ
3. Пример настройки
Описание источника
Источник передаёт в Alpha.Server сообщения об изменениях трёх параметров:
«Temperature» – код параметра «0»;
«Volume» – код параметра «1»;
«Pressure» – код параметра «2».
Каждое сообщение содержит:
текущее значение параметра;
предыдущее значение параметра;
код параметра.
Сообщения буферизуются в источнике, глубина буфера: 10 элементов.
Передача сообщений выполняется по протоколу Modbus в сети TCP.
Настройка Alpha.Server
Настройте Alpha.Server для получения данных из описанного источника:
1. Добавьте в конфигурацию Alpha.Server модуль Data Buffer.
2. В параметрах модуля Data Buffer укажите следующие значения масок:
Маска значения – «0x00000000»;
Маска кода объекта – «0xFFFFFFFF».
12
ALPHA.SERVER. МОДУЛЬ DATA BUFFER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 498 ===
3. ПРИМЕР НАСТРОЙКИ
3. Добавьте в конфигурацию Alpha.Server коммуникационный модуль Modbus TCP Master.
4. В настройках модуля Modbus TCP Master укажите параметры подключения к источнику.
5. В дереве сигналов создайте папку буфера.
6. В папке буфера создайте сигнал типа Uint4.
ALPHA.SERVER. МОДУЛЬ DATA BUFFER. РУКОВОДСТВО АДМИНИСТРАТОРА
13

=== Page 499 ===
3. ПРИМЕР НАСТРОЙКИ
7. Добавьте в созданный сигнал дочерние сигналы: «Val» и «Prev».
8. Добавьте всем созданным в папке буфера сигналам свойство 5000 (Address), и настройте получение
данных из первого элемента буфера источника.
9. Размножьте созданные сигналы: глубина буфера источника - 10 элементов, поэтому требуется
создать 9 копий.
14
ALPHA.SERVER. МОДУЛЬ DATA BUFFER. РУКОВОДСТВО АДМИНИСТРАТОРА

=== Page 500 ===
3. ПРИМЕР НАСТРОЙКИ
10. Для каждого созданного при размножении сигнала (в том числе для дочерних сигналов) измените
значение адреса в свойстве 5000 (Address).
11. В дереве сигналов создайте папку «Temperature».
12. Папке «Temperature» добавьте свойства:
999000 (ObjectType) – значение не указываем;
999001 (ObjectCode) – укажите значение «0».
13. В папке «Temperature» создайте сигнал «Value».
ALPHA.SERVER. МОДУЛЬ DATA BUFFER. РУКОВОДСТВО АДМИНИСТРАТОРА
15

=== Page 501 ===
3. ПРИМЕР НАСТРОЙКИ
14. Сигналу «Value» добавьте свойство 5000 (Address), и поставьте данный сигнал на обслуживание
модулю Data Buffer с параметром «MemberId=(Val)».
15. В папке «Temperature» создайте сигнал «PrevValue».
16. Сигналу «PrevValue» добавьте свойство 5000 (Address), и поставьте данный сигнал на
обслуживание модулю Data Buffer с параметром «MemberId=(Prev)».
17. В дереве сигналов создайте папки «Volume» и «Pressure».
16
ALPHA.SERVER. МОДУЛЬ DATA BUFFER. РУКОВОДСТВО АДМИНИСТРАТОРА