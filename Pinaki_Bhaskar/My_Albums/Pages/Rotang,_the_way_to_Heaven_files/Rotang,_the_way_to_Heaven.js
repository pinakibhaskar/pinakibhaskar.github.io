// Created by iWeb 3.0.4 local-build-20180207

function createMediaStream_id1()
{return IWCreatePhotocast("https://pinakibhaskar.github.io/Pinaki_Bhaskar/My_Albums/Pages/Rotang,_the_way_to_Heaven_files/rss.xml",true);}
function initializeMediaStream_id1()
{createMediaStream_id1().load('https://pinakibhaskar.github.io/Pinaki_Bhaskar/My_Albums/Pages',function(imageStream)
{var entryCount=imageStream.length;var headerView=widgets['widget1'];headerView.setPreferenceForKey(imageStream.length,'entryCount');NotificationCenter.postNotification(new IWNotification('SetPage','id1',{pageIndex:0}));});}
function layoutMediaGrid_id1(range)
{createMediaStream_id1().load('https://pinakibhaskar.github.io/Pinaki_Bhaskar/My_Albums/Pages',function(imageStream)
{if(range==null)
{range=new IWRange(0,imageStream.length);}
IWLayoutPhotoGrid('id1',new IWPhotoGridLayout(2,new IWSize(233,233),new IWSize(233,48),new IWSize(280,296),27,27,0,new IWSize(39,43)),new IWPhotoFrame([IWCreateImage('Rotang,_the_way_to_Heaven_files/Freestyle_01.png'),IWCreateImage('Rotang,_the_way_to_Heaven_files/Freestyle_02.png'),IWCreateImage('Rotang,_the_way_to_Heaven_files/Freestyle_03.png'),IWCreateImage('Rotang,_the_way_to_Heaven_files/Freestyle_06.png'),IWCreateImage('Rotang,_the_way_to_Heaven_files/Freestyle_09.png'),IWCreateImage('Rotang,_the_way_to_Heaven_files/Freestyle_08.png'),IWCreateImage('Rotang,_the_way_to_Heaven_files/Freestyle_07.png'),IWCreateImage('Rotang,_the_way_to_Heaven_files/Freestyle_04.png')],null,2,1.000000,3.000000,3.000000,3.000000,3.000000,22.000000,24.000000,23.000000,25.000000,166.000000,222.000000,166.000000,222.000000,null,null,null,0.100000),imageStream,range,new IWShadow({blurRadius:9,offset:new IWPoint(0.7071,0.7071),color:'#463c3c',opacity:0.300000}),null,1.000000,{backgroundColor:'rgb(0, 0, 0)',reflectionHeight:100,reflectionOffset:2,captionHeight:100,fullScreen:0,transitionIndex:2},'../../Media/slideshow.html','widget1','widget2','widget3')});}
function relayoutMediaGrid_id1(notification)
{var userInfo=notification.userInfo();var range=userInfo['range'];layoutMediaGrid_id1(range);}
function onStubPage()
{var args=window.location.href.toQueryParams();parent.IWMediaStreamPhotoPageSetMediaStream(createMediaStream_id1(),args.id);}
if(window.stubPage)
{onStubPage();}
setTransparentGifURL('../../Media/transparent.gif');function applyEffects()
{var registry=IWCreateEffectRegistry();registry.registerEffects({shadow_0:new IWShadow({blurRadius:4,offset:new IWPoint(1.4142,1.4142),color:'#463c3c',opacity:0.800000})});registry.applyEffects();}
function hostedOnDM()
{return false;}
function onPageLoad()
{IWRegisterNamedImage('comment overlay','../../Media/Photo-Overlay-Comment.png')
IWRegisterNamedImage('movie overlay','../../Media/Photo-Overlay-Movie.png')
loadMozillaCSS('Rotang,_the_way_to_Heaven_files/Rotang,_the_way_to_HeavenMoz.css')
NotificationCenter.addObserver(null,relayoutMediaGrid_id1,'RangeChanged','id1')
fixAllIEPNGs('../../Media/transparent.gif');Widget.onload();fixupIECSS3Opacity('id2');applyEffects()
initializeMediaStream_id1()}
function onPageUnload()
{Widget.onunload();}
