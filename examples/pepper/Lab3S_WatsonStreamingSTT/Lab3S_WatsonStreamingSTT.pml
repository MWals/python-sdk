<?xml version="1.0" encoding="UTF-8" ?>
<Package name="Lab3S_WatsonStreamingSTT" format_version="4">
    <Manifest src="manifest.xml" />
    <BehaviorDescriptions>
        <BehaviorDescription name="behavior" src="behavior_1" xar="behavior.xar" />
    </BehaviorDescriptions>
    <Dialogs />
    <Resources>
        <File name="StreamSTT" src="lib/StreamSTT.py" />
        <File name="__init__" src="lib/ws4py/__init__.py" />
        <File name="__init__" src="lib/ws4py/client/__init__.py" />
        <File name="geventclient" src="lib/ws4py/client/geventclient.py" />
        <File name="threadedclient" src="lib/ws4py/client/threadedclient.py" />
        <File name="tornadoclient" src="lib/ws4py/client/tornadoclient.py" />
        <File name="compat" src="lib/ws4py/compat.py" />
        <File name="exc" src="lib/ws4py/exc.py" />
        <File name="framing" src="lib/ws4py/framing.py" />
        <File name="manager" src="lib/ws4py/manager.py" />
        <File name="messaging" src="lib/ws4py/messaging.py" />
        <File name="__init__" src="lib/ws4py/server/__init__.py" />
        <File name="cherrypyserver" src="lib/ws4py/server/cherrypyserver.py" />
        <File name="geventserver" src="lib/ws4py/server/geventserver.py" />
        <File name="wsgirefserver" src="lib/ws4py/server/wsgirefserver.py" />
        <File name="wsgiutils" src="lib/ws4py/server/wsgiutils.py" />
        <File name="streaming" src="lib/ws4py/streaming.py" />
        <File name="utf8validator" src="lib/ws4py/utf8validator.py" />
        <File name="websocket" src="lib/ws4py/websocket.py" />
        <File name="index" src="html/index.html" />
        <File name="logo-ibm2" src="html/images/logo-ibm2.png" />
        <File name="pause_64" src="html/images/pause_64.png" />
        <File name="recording_64" src="html/images/recording_64.png" />
        <File name="README" src="README.MD" />
        <File name="theWatsonSTTPythonBoxIsSetupToGetTheWatsonSTTAPIKeyFromEitherTheBoxParameters" src="assets/theWatsonSTTPythonBoxIsSetupToGetTheWatsonSTTAPIKeyFromEitherTheBoxParameters.png" />
        <File name="ibm_phg_qi" src="html/ibm_phg_qi.js" />
        <File name="ibm_watson_logo" src="html/images/ibm_watson_logo.jpg" />
        <File name="theWatsonSTTPythonBoxIsSetupToGetTheWatsonSTTAPIKeyFromEitherTheBoxParameters" src="readme_images/theWatsonSTTPythonBoxIsSetupToGetTheWatsonSTTAPIKeyFromEitherTheBoxParameters.png" />
    </Resources>
    <Topics />
    <IgnoredPaths />
    <Translations auto-fill="en_US">
        <Translation name="translation_de_DE" src="translations/translation_de_DE.ts" language="de_DE" />
        <Translation name="translation_en_US" src="translations/translation_en_US.ts" language="en_US" />
        <Translation name="translation_es_ES" src="translations/translation_es_ES.ts" language="es_ES" />
        <Translation name="translation_fr_FR" src="translations/translation_fr_FR.ts" language="fr_FR" />
        <Translation name="translation_it_IT" src="translations/translation_it_IT.ts" language="it_IT" />
        <Translation name="translation_ru_RU" src="translations/translation_ru_RU.ts" language="ru_RU" />
    </Translations>
</Package>
