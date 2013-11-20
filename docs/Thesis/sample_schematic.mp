outputtemplate := "%j-%c.mps";

ahlength := 5;
linejoin := mitered;
thickwidth := 2;
mediumwidth := 1.2;
thinwidth := .6;

def thinpen  = withpen pencircle scaled thinwidth enddef;
def mediumpen  = withpen pencircle scaled mediumwidth enddef;
def thickpen = withpen pencircle scaled thickwidth enddef;
def darkred = (.8,0,0) enddef;
def darkgreen = (0,.8,0) enddef;
def darkblue = (0,0,.8) enddef;
extra_beginfig := extra_beginfig & "drawoptions(mediumpen);";

vardef arrow(expr p) =
  drawarrow p cutafter fullcircle scaled 4mediumwidth shifted point length p of p;
enddef;

vardef bluearrow(expr p) =
  drawarrow p cutafter fullcircle scaled 4mediumwidth shifted point length p of p mediumpen withcolor darkblue;
enddef;

vardef redarrow(expr p) =
  drawarrow p cutafter fullcircle scaled 4mediumwidth shifted point length p of p mediumpen withcolor red;
enddef;

cktS := 2cm;
vardef putlabel(expr a,b,y,z) =
  if z="e": label.rt(y, (a+.b*right) scaled cktS+down); fi
  if z="w": label.lft(y,(a+.b*left) scaled cktS+down); fi
  if z="n": label.top(y,(a+.b*up) scaled cktS); fi
  if z="s": label.bot(y,(a+.b*down) scaled cktS); fi
enddef;

vardef cktResistor(suffix $)(expr w,x,y,z) =
  pair $.a; $.a = if pair(w): w; else: x+((1,0) rotated w); fi
  pair $.b; $.b = if pair(x): x; else: w+((1,0) rotated x); fi
  draw ($.a--((-6,0)--(-5,-3)--(-3,3)--(-1,-3)--(1,3)--(3,-3)--(5,3)--(6,0)) scaled 1/24 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b]--$.b) scaled cktS mediumpen withcolor darkblue;
  putlabel(.5[$.a,$.b],.15,y,z);
enddef;

vardef cktPhotoResistor(suffix $)(expr w,x,y,z) =
  pair $.a; $.a = if pair(w): w; else: x+((1,0) rotated w); fi
  pair $.b; $.b = if pair(x): x; else: w+((1,0) rotated x); fi
  draw ($.a--((-6,0)--(-5,-3)--(-3,3)--(-1,-3)--(1,3)--(3,-3)--(5,3)--(6,0)) scaled 1/24 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b]--$.b) scaled cktS mediumpen withcolor darkblue;
  drawarrow ((-2,6)--(2,-6)) scaled (1/24) zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b] scaled cktS withcolor darkblue;
  putlabel(.5[$.a,$.b],.25,y,z);
enddef;

vardef cktPot(suffix $)(expr w,x,y,z) =
  pair $.a; $.a = if pair(w): w; else: x+((1,0) rotated w); fi
  pair $.b; $.b = if pair(x): x; else: w+((1,0) rotated x); fi
  draw ($.a--((-5,0)--(-4,-3)--(-2,3)--(0,-3)--(2,3)--(4,-3)--(5,0)) scaled 1/24 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b]--$.b) scaled cktS mediumpen withcolor darkblue;
  drawarrow ((0,-10)--(0,-4)) scaled 1/24 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b] scaled cktS mediumpen withcolor darkblue;
  putlabel(.5[$.a,$.b],.15,y,z);
enddef;

vardef cktInvPot(suffix $)(expr w,x,y,z) =
    pair $.a; $.a = if pair(w): w; else: x+((1,0) rotated w); fi
    pair $.b; $.b = if pair(x): x; else: w+((1,0) rotated x); fi
    draw ($.a--((-5,0)--(-4,-3)--(-2,3)--(0,-3)--(2,3)--(4,-3)--(5,0)) scaled 1/24 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b]--$.b) scaled cktS mediumpen withcolor darkblue;
    drawarrow ((0,10)--(0,4)) scaled 1/24 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b] scaled cktS mediumpen withcolor darkblue;
    putlabel(.5[$.a,$.b],.15,y,z);
enddef;

vardef cktInductor(suffix $)(expr w,x,y,z) =
  pair $.a; $.a = if pair(w): w; else: x+((1,0) rotated w); fi
  pair $.b; $.b = if pair(x): x; else: w+((1,0) rotated x); fi
  draw ($.a--((-5,0)..controls (-5,4) and (-1,4)..(-1,0)..controls (-1,-3) and (-2,-3)..(-2,0)..controls (-2,4) and (2,4)..(2,0)..controls (2,-3) and (1,-3)..(1,0)..controls (1,4) and (5,4)..(5,0)) scaled 1/20 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b]--$.b) scaled cktS mediumpen withcolor darkblue;
  putlabel(.5[$.a,$.b],.15,y,z);
enddef;

vardef cktCapacitor(suffix $)(expr w,x,y,z) =
  pair $.a; $.a = if pair(w): w; else: x+((1,0) rotated w); fi
  pair $.b; $.b = if pair(x): x; else: w+((1,0) rotated x); fi
  draw ($.a--((-5,0)--(-1,0)--(-1,4)--(-1,-4)) scaled 1/24 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b]) scaled cktS mediumpen withcolor darkblue;
  draw (((1,-4)--(1,4)--(1,0)--(5,0)) scaled 1/24 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b]--$.b) scaled cktS mediumpen withcolor darkblue;
  putlabel(.5[$.a,$.b],.2,y,z);
enddef;

vardef cktGround(suffix $)(expr w,x) =
  pair $.a; $.a = if pair(w): w; else: x+((.5,0) rotated w); fi
  pair $.b; $.b = if pair(x): x; else: w+((.5,0) rotated x); fi
  draw ($.a--.5[$.a,$.b]) scaled cktS mediumpen withcolor darkblue;
  draw (((0,3)--(0,-3)) scaled 1/24 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b]) scaled cktS mediumpen withcolor darkblue;
  draw (((2,2)--(2,-2)) scaled 1/24 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b]) scaled cktS mediumpen withcolor darkblue;
  draw (((4,1)--(4,-1)) scaled 1/24 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b]) scaled cktS mediumpen withcolor darkblue;
enddef;

vardef cktDiode(suffix $)(expr w,x) =
  pair $.a; $.a = if pair(w): w; else: x+((1,0) rotated w); fi
  pair $.b; $.b = if pair(x): x; else: w+((1,0) rotated x); fi
  draw ($.a--$.b) scaled cktS mediumpen withcolor darkblue;
  draw (((-2,3)--(-2,-3)) scaled 1/24 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b]) scaled cktS mediumpen withcolor darkblue;
  fill (((2,3)--(2,-3)--(-2,0)--cycle) scaled 1/24 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b]) scaled cktS mediumpen withcolor darkblue;
enddef;

vardef cktVSrc(suffix $)(expr w,x,y,z) =
  pair $.a; $.a = if pair(w): w; else: x+((1,0) rotated w); fi
  pair $.b; $.b = if pair(x): x; else: w+((1,0) rotated x); fi
  draw fullcircle scaled 0.5 shifted .5[$.a,$.b] scaled cktS mediumpen withcolor darkblue;
  draw ($.a--(-.25,0) zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$a,$b]) scaled cktS mediumpen withcolor darkblue;
  draw ($.b--(.25,0) zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$a,$b]) scaled cktS mediumpen withcolor darkblue;
  draw (((0,-1)--(0,1)) shifted (2,0) scaled 1/16 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b]) scaled cktS mediumpen withcolor darkblue;
  draw (((-1,0)--(1,0)) shifted (2,0) scaled 1/16 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b]) scaled cktS mediumpen withcolor darkblue;
  draw (((0,-1)--(0,1)) shifted (-2,0) scaled 1/16 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b]) scaled cktS mediumpen withcolor darkblue;
  putlabel(.5[$.a,$.b],.3,y,z);
enddef;

vardef cktCVSrc(suffix $)(expr w,x,y,z) =
  pair $.a; $.a = if pair(w): w; else: x+((1,0) rotated w); fi
  pair $.b; $.b = if pair(x): x; else: w+((1,0) rotated x); fi
  draw ((-5,0)--(0,-4)--(5,0)--(0,4)--cycle) scaled 1/16 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b] scaled cktS mediumpen withcolor darkblue;
  draw ($.a--(-5/16,0) zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$a,$b]) scaled cktS mediumpen withcolor darkblue;
  draw ($.b--(5/16,0) zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$a,$b]) scaled cktS mediumpen withcolor darkblue;
  draw (((0,-1)--(0,1)) shifted (2,0) scaled 1/16 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b]) scaled cktS mediumpen withcolor darkblue;
  draw (((-1,0)--(1,0)) shifted (2,0) scaled 1/16 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b]) scaled cktS mediumpen withcolor darkblue;
  draw (((0,-1)--(0,1)) shifted (-2,0) scaled 1/16 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b]) scaled cktS mediumpen withcolor darkblue;
  putlabel(.5[$.a,$.b],.3,y,z);
enddef;

vardef cktISrc(suffix $)(expr w,x,y,z) =
  pair $.a; $.a = if pair(w): w; else: x+((1,0) rotated w); fi
  pair $.b; $.b = if pair(x): x; else: w+((1,0) rotated x); fi
  draw fullcircle scaled 0.5 shifted .5[$.a,$.b] scaled cktS mediumpen withcolor darkblue;
  draw ($.a--(-.25,0) zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$a,$b]) scaled cktS mediumpen withcolor darkblue;
  draw ($.b--(.25,0) zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$a,$b]) scaled cktS mediumpen withcolor darkblue;
  drawarrow (((-2.5,0)--(2.5,0)) scaled 1/16 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b]) scaled cktS mediumpen withcolor darkblue;
  putlabel(.5[$.a,$.b],.3,y,z);
enddef;

vardef cktCISrc(suffix $)(expr w,x,y,z) =
  pair $.a; $.a = if pair(w): w; else: x+((1,0) rotated w); fi
  pair $.b; $.b = if pair(x): x; else: w+((1,0) rotated x); fi
  draw ((-5,0)--(0,-4)--(5,0)--(0,4)--cycle) scaled 1/16 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b] scaled cktS mediumpen withcolor darkblue;
  draw ($.a--(-5/16,0) zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$a,$b]) scaled cktS mediumpen withcolor darkblue;
  draw ($.b--(5/16,0) zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$a,$b]) scaled cktS mediumpen withcolor darkblue;
  drawarrow (((-2.5,0)--(2.5,0)) scaled 1/16 zscaled (($.b-$.a)/length($.b-$.a)) shifted .5[$.a,$.b]) scaled cktS mediumpen withcolor darkblue;
  putlabel(.5[$.a,$.b],.3,y,z);
enddef;

vardef cktOpAmpN(suffix $)(expr w,x) =
  pair $.a; $.a = if pair(w): w; else: x+((-1,.15) rotated w); fi
  pair $.c; $.c = if pair(x): x; else: w+((1,-.15) rotated x); fi
  pair $.b; $.b = $.c+(($.a-$.c) rotated (2*angle(1,.15)));
  draw ((0,0)--(.2,0)--(.2,-.3)--(0,-.3)--(.2,-.3)--(.2,-.48)--(.8,-.15)--(1,-.15)--(.8,-.15)--(.2,.18)--(.2,0)) rotated angle ($.c-.5[$.a,$.b]) shifted $.a scaled cktS mediumpen withcolor darkblue;
  draw ((0,1/20)--(0,-1/20)) shifted (.32,-0/100)
    rotated angle ($.c-.5[$.a,$.b]) shifted $.a scaled (cktS) withcolor darkblue;
  draw ((1/20,0)--(-1/20,0)) shifted (.32,-0/100)
    rotated angle ($.c-.5[$.a,$.b]) shifted $.a scaled (cktS) withcolor darkblue;
  draw ((1/20,0)--(-1/20,0)) shifted (.32,-.3+0/100)
    rotated angle ($.c-.5[$.a,$.b]) shifted $.a scaled (cktS) withcolor darkblue;
enddef;

vardef cktOpAmpS(suffix $)(expr w,x) =
  pair $.a; $.a = if pair(w): w; else: x+((-1,-.15) rotated w); fi
  pair $.c; $.c = if pair(x): x; else: w+((1,.15) rotated x); fi
  pair $.b; $.b = $.c+(($.a-$.c) rotated (2*angle(1,-.15)));
  draw ((0,0)--(.2,0)--(.2,.3)--(0,.3)--(.2,.3)--(.2,.48)--(.8,.15)--(1,.15)--(.8,.15)--(.2,-.18)--(.2,0)) rotated angle ($.c-.5[$.a,$.b]) shifted $.a scaled cktS mediumpen withcolor darkblue;
  draw ((0,1/20)--(0,-1/20)) shifted (.32,.3-0/100)
    rotated angle ($.c-.5[$.a,$.b]) shifted $.a scaled (cktS) withcolor darkblue;
  draw ((1/20,0)--(-1/20,0)) shifted (.32,.3-0/100)
    rotated angle ($.c-.5[$.a,$.b]) shifted $.a scaled (cktS) withcolor darkblue;
  draw ((1/20,0)--(-1/20,0)) shifted (.32,0/100)
    rotated angle ($.c-.5[$.a,$.b]) shifted $.a scaled (cktS) withcolor darkblue;
enddef;

vardef cktInvOpAmpN(suffix $)(expr w,x) =
  pair $.a; $.a = if pair(w): w; else: x+((-1,.15) rotated w); fi
  pair $.c; $.c = if pair(x): x; else: w+((1,-.15) rotated x); fi
  pair $.b; $.b = $.c+(($.a-$.c) rotated (2*angle(1,.15)));
  draw ((0,0)--(.2,0)--(.2,-.3)--(0,-.3)--(.2,-.3)--(.2,-.48)--(.8,-.15)--(1,-.15)--(.8,-.15)--(.2,.18)--(.2,0)) rotated angle ($.c-.5[$.a,$.b]) shifted $.a scaled cktS mediumpen withcolor darkblue;
  draw ((0,1/20)--(0,-1/20)) shifted (.32,-.3-0/100)
    rotated angle ($.c-.5[$.a,$.b]) shifted $.a scaled (cktS) withcolor darkblue;
  draw ((1/20,0)--(-1/20,0)) shifted (.32,-0/100)
    rotated angle ($.c-.5[$.a,$.b]) shifted $.a scaled (cktS) withcolor darkblue;
  draw ((1/20,0)--(-1/20,0)) shifted (.32,-.3+0/100)
    rotated angle ($.c-.5[$.a,$.b]) shifted $.a scaled (cktS) withcolor darkblue;
enddef;

vardef cktInvOpAmpS(suffix $)(expr w,x) =
  pair $.a; $.a = if pair(w): w; else: x+((-1,-.15) rotated w); fi
  pair $.c; $.c = if pair(x): x; else: w+((1,.15) rotated x); fi
  pair $.b; $.b = $.c+(($.a-$.c) rotated (2*angle(1,-.15)));
  draw ((0,0)--(.2,0)--(.2,.3)--(0,.3)--(.2,.3)--(.2,.48)--(.8,.15)--(1,.15)--(.8,.15)--(.2,-.18)--(.2,0)) rotated angle ($.c-.5[$.a,$.b]) shifted $.a scaled cktS mediumpen withcolor darkblue;
  draw ((0,1/20)--(0,-1/20)) shifted (.32,-0/100)
    rotated angle ($.c-.5[$.a,$.b]) shifted $.a scaled (cktS) withcolor darkblue;
  draw ((1/20,0)--(-1/20,0)) shifted (.32,.3-0/100)
    rotated angle ($.c-.5[$.a,$.b]) shifted $.a scaled (cktS) withcolor darkblue;
  draw ((1/20,0)--(-1/20,0)) shifted (.32,0/100)
    rotated angle ($.c-.5[$.a,$.b]) shifted $.a scaled (cktS) withcolor darkblue;
enddef;

vardef cktWire(expr a) =
  draw a scaled cktS mediumpen withcolor darkblue;
enddef;

vardef cktVoltage(expr w,x,ll) =
  draw ((-.05,0)--(.05,0)) shifted w scaled cktS mediumpen withcolor darkblue;
  draw ((0,-.05)--(0,.05)) shifted w scaled cktS mediumpen withcolor darkblue;
  draw ((-.05,0)--(.05,0)) shifted x scaled cktS mediumpen withcolor darkblue;
  label(ll,.5[x,w] scaled cktS);
enddef;

vardef cktCurrent(expr w,x,y,z) =
  pair a; a = if pair(w): w; else: x+((1,0) rotated w); fi
  pair b; b = if pair(x): x; else: w+((1,0) rotated x); fi
  draw (a--b) scaled cktS mediumpen withcolor darkblue;
  drawarrow (a--.75[a,b]) scaled cktS mediumpen withcolor darkblue;
%  label.top(ll,x scaled cktS+2up);
  putlabel(.5[a,b],.05,y,z);
enddef;

beginfig(22)
numeric x;
x := 0.5; % op amp follower
numeric y;
y := 0.5; % ground separation
cktPot(ra, (0,0), (0,1), btex ~ etex, "w");
cktOpAmpN(oa, (0.5, 0.5), 0);
cktWire(oa.a--(0.25,0.5));
cktWire(oa.c--oa.c+(0,-x)--oa.b+(0,-x+.15)--oa.b);
numeric width, height;
width := 1.25;
height := .75;
pair corner;
corner := oa.c + (.5, height/2);
cktWire(corner--corner+(width,0)--corner+(width,-height)--corner+(0,-height)--corner);
label(btex Motor etex, (corner+(width/2,-height/2)) scaled cktS);
cktInvOpAmpN(ob, 180, (oa.c+(width+1, 0)));
cktInvPot(rb, ob.b+(0.5,-0.5),ob.b+(0.5,0.5), btex ~ etex, "e");
cktWire(ob.b--ob.b+(0.25,0));
cktWire(ob.c--ob.c+(0,-x)--ob.a+(0,-x+.15)--ob.a);
cktWire(oa.c--corner+(0,-height/2));
cktWire(ob.c--corner+(width,-height/2));
cktGround(ga, ra.a, ra.a+(0,-y));
cktGround(gb, rb.a, rb.a+(0,-y));
cktWire(ra.b--ra.b+(0,y/2));
cktWire(rb.b--rb.b+(0,y/2));
label.top(btex $+10V$ etex, (ra.b + (0,y/2)) scaled cktS);
label.top(btex $+10V$ etex, (rb.b + (0,y/2)) scaled cktS);
label.rt(btex $+$ etex, (corner+(0,-height/2)) scaled cktS);
label.lft(btex $-$ etex, (corner+(width,-height/2)) scaled cktS);
label.lft(btex Control Pot etex, (-.25, .5) scaled cktS);
label.rt(btex Motor Pot etex, (0.5[rb.a, rb.b] + (.25, 0)) scaled cktS);

endfig;

end
