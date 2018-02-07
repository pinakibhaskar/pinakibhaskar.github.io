// Created by iWeb 3.0.4 local-build-20180207

function createMediaStream_id1()
{return IWCreateMediaCollection("https://pinakibhaskar.github.io/Pinaki_Bhaskar/My_Albums/My_Albums_files/rss.xml",true,255,["No photos yet","%d photo","%d photos"],["","%d clip","%d clips"]);}
function initializeMediaStream_id1()
{createMediaStream_id1().load('https://pinakibhaskar.github.io/Pinaki_Bhaskar/My_Albums',function(imageStream)
{var entryCount=imageStream.length;var headerView=widgets['widget7'];headerView.setPreferenceForKey(imageStream.length,'entryCount');NotificationCenter.postNotification(new IWNotification('SetPage','id1',{pageIndex:0}));});}
function layoutMediaGrid_id1(range)
{createMediaStream_id1().load('https://pinakibhaskar.github.io/Pinaki_Bhaskar/My_Albums',function(imageStream)
{if(range==null)
{range=new IWRange(0,imageStream.length);}
IWLayoutPhotoGrid('id1',new IWPhotoGridLayout(2,new IWSize(287,215),new IWSize(287,41),new IWSize(344,271),27,27,0,new IWSize(108,95)),new IWPhotoFrame([IWCreateImage('My_Albums_files/spiralbook-creme_ul.png'),IWCreateImage('My_Albums_files/spiralbook-creme_top.png'),IWCreateImage('My_Albums_files/spiralbook-creme_ur.png'),IWCreateImage('My_Albums_files/spiralbook-creme_right.png'),IWCreateImage('My_Albums_files/spiralbook-creme_lr.png'),IWCreateImage('My_Albums_files/spiralbook-creme_bottom.png'),IWCreateImage('My_Albums_files/spiralbook-creme_ll.png'),IWCreateImage('My_Albums_files/spiralbook-creme_left.png')],null,1,1.000000,15.000000,0.000000,0.000000,0.000000,83.000000,40.000000,40.000000,55.000000,106.000000,40.000000,40.000000,32.000000,null,null,null,0.300000),imageStream,range,(null),null,1.000000,null,'../Media/slideshow.html','widget7',null,'widget8',{showTitle:true,showMetric:true})});}
function relayoutMediaGrid_id1(notification)
{var userInfo=notification.userInfo();var range=userInfo['range'];layoutMediaGrid_id1(range);}
function onStubPage()
{var args=window.location.href.toQueryParams();parent.IWMediaStreamPhotoPageSetMediaStream(createMediaStream_id1(),args.id);}
if(window.stubPage)
{onStubPage();}
setTransparentGifURL('../Media/transparent.gif');function applyEffects()
{var registry=IWCreateEffectRegistry();registry.registerEffects({shadow_0:new IWShadow({blurRadius:4,offset:new IWPoint(1.4142,1.4142),color:'#463c3c',opacity:0.800000}),shadow_1:new IWShadow({blurRadius:10,offset:new IWPoint(0.0000,0.0000),color:'#463c3c',opacity:0.750000}),shadow_2:new IWShadow({blurRadius:4,offset:new IWPoint(1.4142,1.4142),color:'#463c3c',opacity:0.750000})});registry.applyEffects();}
function hostedOnDM()
{return false;}
function onPageLoad()
{IWRegisterNamedImage('comment overlay','../Media/Photo-Overlay-Comment.png')
IWRegisterNamedImage('movie overlay','../Media/Photo-Overlay-Movie.png')
loadMozillaCSS('My_Albums_files/My_AlbumsMoz.css')
NotificationCenter.addObserver(null,relayoutMediaGrid_id1,'RangeChanged','id1')
adjustLineHeightIfTooBig('id2');adjustFontSizeIfTooBig('id2');fixAllIEPNGs('../Media/transparent.gif');Widget.onload();fixupAllIEPNGBGs();fixupIECSS3Opacity('id3');applyEffects()
initializeMediaStream_id1()}
function onPageUnload()
{Widget.onunload();}
