// Created by iWeb 3.0.4 local-build-20180207

setTransparentGifURL('Media/transparent.gif');function applyEffects()
{var registry=IWCreateEffectRegistry();registry.registerEffects({shadow_0:new IWShadow({blurRadius:4,offset:new IWPoint(1.4142,1.4142),color:'#463c3c',opacity:0.800000}),shadow_2:new IWShadow({blurRadius:4,offset:new IWPoint(1.4142,1.4142),color:'#463c3c',opacity:0.750000}),shadow_1:new IWShadow({blurRadius:4,offset:new IWPoint(1.4142,1.4142),color:'#463c3c',opacity:0.800000})});registry.applyEffects();}
function hostedOnDM()
{return false;}
function onPageLoad()
{loadMozillaCSS('Research_files/ResearchMoz.css')
adjustLineHeightIfTooBig('id1');adjustFontSizeIfTooBig('id1');adjustLineHeightIfTooBig('id2');adjustFontSizeIfTooBig('id2');adjustLineHeightIfTooBig('id3');adjustFontSizeIfTooBig('id3');adjustLineHeightIfTooBig('id4');adjustFontSizeIfTooBig('id4');adjustLineHeightIfTooBig('id5');adjustFontSizeIfTooBig('id5');fixAllIEPNGs('Media/transparent.gif');Widget.onload();fixupIECSS3Opacity('id6');applyEffects()}
function onPageUnload()
{Widget.onunload();}
