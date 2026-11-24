(function(){
var $=function(i){return document.getElementById(i)};
var API=window.__API_BASE__||'';
function ev(k){try{fetch(API+'/api/event',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({kind:k,src:new URLSearchParams(location.search).get('src')||'direct',page:'afg'})})}catch(e){}}
var ST=['AL','AK','AZ','AR','CA','CO','CT','DE','DC','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY','PR','GU','VI','AS','MP'];
ST.forEach(function(s){var o=document.createElement('option');o.value=s;o.textContent=s;$('dst').appendChild(o)});
var D=null,US=null,timer=null,last=[],A={item:'ppe',age:'',calls:'',bud:'',fund:[],hz:[]},TAB=0,made=false;
function fmt(n){return Number(n).toLocaleString('en-US')}
function getJ(u){return fetch(API+u).then(function(r){return r.json()})}
function search(){var q=$('dq').value.trim();if(q.length<2){$('dres').innerHTML='';return}
 getJ('/api/dept?q='+encodeURIComponent(q)+'&st='+$('dst').value).then(function(j){US=j.us;last=j.results;var box=$('dres');box.innerHTML='';
  j.results.slice(0,8).forEach(function(d,i){var b=document.createElement('button');b.type='button';b.className='dpick';
   var s1=document.createElement('strong');s1.textContent=d.name;var s2=document.createElement('span');s2.textContent='  '+d.city+', '+d.state+' · '+d.type;b.appendChild(s1);b.appendChild(s2);
   b.addEventListener('click',function(){pick(i)});box.appendChild(b)});
  var m=document.createElement('button');m.type='button';m.className='dpick alt';m.textContent=j.results.length?'Not listed? Use "'+q+'" as my department':'Not in the national registry. Use "'+q+'" as my department';
  m.addEventListener('click',function(){last=[{name:q,city:q,state:$('dst').value||'',county:'',type:'Volunteer',stations:0,career:0,volunteer:0,ppc:0,county_econ:null,state_econ:j.state_econ}];pick(0)});box.appendChild(m)})
 .catch(function(){$('dres').textContent='Search is unavailable right now. Please try again in a minute.'})}
$('dq').addEventListener('input',function(){clearTimeout(timer);timer=setTimeout(search,200)});
$('dst').addEventListener('change',search);
function pick(i){D=last[i];$('dres').innerHTML='';$('dq').value=D.name;
 var k=$('known');k.innerHTML='';var tot=D.career+D.volunteer+D.ppc,e=D.county_econ,se=D.state_econ;
 var facts=[['Department',D.name],['Type',D.type],['Location',(D.city?D.city+', ':'')+D.state+(D.county?' · '+D.county+' County':'')],['Stations',D.stations?String(D.stations):'not listed'],['Firefighters',tot?fmt(tot):'not listed']];
 if(e){if(e.pop)facts.push(['County population',fmt(e.pop)]);if(e.pov!=null)facts.push(['County poverty rate',e.pov+'% (U.S. '+US.pov+'%)']);if(e.inc)facts.push(['County household income','$'+fmt(e.inc)+' (U.S. $'+fmt(US.inc)+')'])}
 else if(se){facts.push(['State poverty rate',se.pov+'% (U.S. '+US.pov+'%)']);facts.push(['State household income','$'+fmt(se.inc)])}
 facts.forEach(function(f){var li=document.createElement('li');var b=document.createElement('span');b.className='kl';b.textContent=f[0];li.appendChild(b);li.appendChild(document.createTextNode(f[1]));k.appendChild(li)});
 D._facts=facts.length;$('dstep2').hidden=false;
 if(!A.fund.length&&/volunteer/i.test(D.type)){} 
 build();if(!made){made=true;ev('draft_made')}
 $('dstep2').scrollIntoView({behavior:'smooth',block:'start'})}
Array.prototype.forEach.call(document.querySelectorAll('#dz .qg'),function(g){var key=g.getAttribute('data-q'),multi=g.classList.contains('multi');
 if(!multi&&!g.querySelector('[aria-pressed=true]'))g.querySelector('button').setAttribute('aria-pressed','true');
 Array.prototype.forEach.call(g.querySelectorAll('button'),function(b){if(!b.hasAttribute('aria-pressed'))b.setAttribute('aria-pressed','false');
  b.addEventListener('click',function(){var v=b.getAttribute('data-v');
   if(multi){var on=b.getAttribute('aria-pressed')!=='true';b.setAttribute('aria-pressed',on?'true':'false');A[key]=Array.prototype.filter.call(g.querySelectorAll('button[aria-pressed=true]'),function(){return 1}).map(function(x){return x.getAttribute('data-v')})}
   else{Array.prototype.forEach.call(g.querySelectorAll('button'),function(x){x.setAttribute('aria-pressed','false')});b.setAttribute('aria-pressed','true');A[key]=v}
   if(D)build()})})});
function list(a){return a.length<2?a.join(''):a.slice(0,-1).join(', ')+' and '+a[a.length-1]}
var F=function(t){return '\u27E6'+t+'\u27E7'};
var IT={
 ppe:{meet:'NFPA 1851 (now part of NFPA 1850) care and retirement requirements',what:'turnout gear',full:'sets of structural turnout gear (coat, pants, helmet, hood, gloves and boots)',std:'NFPA 1851 (now part of NFPA 1850) requires structural gear to be retired 10 years from its manufacture date',risk:'Gear past its service life loses thermal protection and moisture-barrier performance, which puts members at risk of burns and heat stress on every interior attack.',use:'every structure fire, vehicle fire and overhaul'},
 scba:{meet:'current NFPA 1981 (NFPA 1970) SCBA requirements',what:'SCBA',full:'self-contained breathing apparatus with spare cylinders and individually fitted face pieces',std:'SCBA must meet NFPA 1981 (now part of NFPA 1970), and composite cylinders reach the end of their DOT service life at 15 years',risk:'An air pack that fails or runs short inside a working fire is a mayday. Older packs lack current low-air alarms, integrated PASS devices and universal rescue connections.',use:'every interior attack, search, ventilation and overhaul'},
 radio:{meet:'our county radio interoperability requirements',what:'portable radios',full:'portable radios with chargers, spare batteries and speaker-mics',std:'radios must work on the system used by our county dispatch and mutual aid partners',risk:'When a member on the fireground cannot reach command or dispatch, a mayday can go unheard. Dead spots and failing batteries are a known life-safety problem for our crews.',use:'every call, from medical assists to working fires and mutual aid'},
 equip:{meet:'current NFPA requirements for this equipment',what:'equipment',full:F('list the equipment, e.g. thermal imaging camera, attack hose and nozzles, battery extrication tools'),std:'equipment must meet the NFPA standard for its type',risk:'Without this equipment our crews take longer to find victims, locate fire in walls and ceilings, and free trapped patients.',use:'structure fires, vehicle crashes and searches'},
 train:{meet:'the NFPA 1001 (NFPA 1010) standard for interior firefighters',what:'training',full:'Firefighter I and II certification courses (NFPA 1001, now part of NFPA 1010), including instructor costs, books and burn-building fees',std:'members who enter burning buildings should be trained to at least Firefighter I',risk:'Untrained members on the fireground are a danger to themselves and their crews, and limit what we can safely do on arrival.',use:'every call our members respond to'},
 well:{meet:'the NFPA 1582 medical evaluation standard',what:'annual medical exams',full:'annual NFPA 1582 medical exams, including cardiac and cancer screening, for all active members',std:'NFPA 1582 sets the medical evaluation standard for fire department members',risk:'Sudden cardiac events are a leading cause of on-duty firefighter deaths, and cancer is now the top career-related threat to firefighters.',use:'keeping every member fit for duty'}};
function build(){
 var it=IT[A.item],e=D.county_econ||D.state_econ,area=D.county_econ?D.county+' County':(D.state||F('state')),tot=D.career+D.volunteer+D.ppc;
 var dtype=/volunteer/i.test(D.type)?'all-volunteer':(/combination|mostly/i.test(D.type)?'combination':D.type.toLowerCase());
 var who=D.name+(/^[aeiou]/.test(dtype)?' is an ':' is a ')+dtype+' fire department';
 var nTxt=tot?fmt(tot):F('number');
 var fin=who+' serving '+(D.city&&D.city!==D.name?D.city:F('town'))+' and the surrounding area in '+area+(D.state?', '+D.state:'')+'. We operate '+(D.stations||F('number'))+' station'+(D.stations==1?'':'s')+' with '+(tot?fmt(tot):F('number'))+' active members, and we answer '+(A.calls||F('number'))+' calls a year. ';
 if(e&&e.pov!=null&&US){fin+='According to the U.S. Census Bureau, '+e.pov+'% of '+area+' residents live below the poverty line, '+(e.pov>US.pov?'above':'below')+' the national rate of '+US.pov+'%. '}
 if(e&&e.inc&&US){var pct=Math.round(Math.abs(1-e.inc/US.inc)*100);fin+='Median household income is $'+fmt(e.inc)+', '+pct+'% '+(e.inc<US.inc?'below':'above')+' the national median of $'+fmt(US.inc)+'. '}
 fin+='Our yearly operating budget is '+(A.bud||F('$ amount'))+', funded through '+(A.fund.length?list(A.fund):F('your funding sources'))+'. Fuel, insurance, apparatus maintenance, utilities and required testing take '+F('share, e.g. nearly all')+' of that budget, leaving little for capital purchases. ';
 fin+='Replacing '+it.what+' for '+nTxt+' members costs about '+F('$ total from your quotes')+', more than we can raise in '+F('number')+' years. We have tried to fund this locally through '+F('e.g. boot drives, a budget request to the town')+', but '+F('what happened')+'. Without AFG funding, we will '+F('consequence, e.g. keep members in gear past its service life')+'.';
 var proj='We are requesting '+nTxt+' '+it.full+'. Our current '+it.what+' is '+(A.age||F('age'))+' and '+F('condition, e.g. failed inspection, past service life, parts no longer available')+'. '+it.std.charAt(0).toUpperCase()+it.std.slice(1)+'. '+it.risk+(A.hz.length?' Our first-due area includes '+list(A.hz)+', which drives the type and number of calls we run.':'')+' ';
 proj+='This request covers '+nTxt+' members who '+F('e.g. are interior-qualified / respond on every call')+'. We will buy only what those members need, nothing extra.';
 var cb='We collected '+F('number')+' written quotes and selected '+F('vendor or "the lowest qualified quote"')+' at '+F('$ per unit')+' per unit, for a total of '+F('$ total')+'. The department will pay its required cost share of '+F('5% if you protect 20,000 people or fewer, 10% if 20,001 to 1 million')+' from '+F('source, e.g. our equipment reserve')+'. ';
 cb+='The '+it.what+' will be used on '+it.use+'. With '+(A.calls||F('number'))+' calls a year over '+F('expected service life')+' years of service, the cost works out to about '+F('$')+' per call. We give and receive mutual aid with '+F('names or number of departments')+', so this purchase also protects members from neighboring companies working beside us.';
 var soe='With new '+it.what+', our members will be able to '+F('what changes on calls, e.g. make a safe interior attack on arrival instead of waiting for mutual aid')+'. Today we '+F('current workaround, e.g. share packs / borrow from neighboring departments')+'. ';
 soe+='This grant will improve firefighter safety on '+it.use+', reduce the chance of injury or a line-of-duty death, and let us meet '+it.meet+'. We will put the '+it.what+' in service within '+F('number')+' days of delivery, train all members on it, log inspections '+F('monthly / after each use')+', and report incidents through '+F('NFIRS or NERIS')+'. Residents of '+(D.city&&D.city!==D.name?D.city:F('town'))+' will see '+F('benefit, e.g. faster, safer fire attack')+'.';
 var secs=[['Financial Need',fin],['Project Description',proj],['Cost-Benefit',cb],['Statement of Effect',soe]];
 window.__draftText=secs.map(function(s){return s[0].toUpperCase()+'\n'+s[1].replace(/\u27E6/g,'[').replace(/\u27E7/g,']')}).join('\n\n');
 var tabs=$('dtabs');tabs.innerHTML='';var out=$('dsecs');out.innerHTML='';var blanks=0;
 secs.forEach(function(s,i){var b=0;var p=document.createElement('p');
  s[1].split(/(\u27E6[^\u27E7]*\u27E7)/).forEach(function(part){if(/^\u27E6/.test(part)){b++;var m=document.createElement('mark');m.textContent='['+part.slice(1,-1)+']';p.appendChild(m)}else if(part)p.appendChild(document.createTextNode(part))});
  blanks+=b;var t=document.createElement('button');t.type='button';t.setAttribute('role','tab');t.setAttribute('aria-selected',i===TAB?'true':'false');t.textContent=s[0];
  t.addEventListener('click',function(){TAB=i;build()});tabs.appendChild(t);
  if(i===TAB){var w=document.createElement('div');w.className='dsec';w.appendChild(p);var c=document.createElement('div');c.className='note';c.textContent=s[1].replace(/[\u27E6\u27E7]/g,'').length.toLocaleString()+' of 4,000 characters · '+b+' blank'+(b===1?'':'s')+' to fill';w.appendChild(c);out.appendChild(w)}});
 var how=$('how');how.innerHTML='';var h=document.createElement('p');var hb=document.createElement('b');hb.textContent='Done. ';h.appendChild(hb);
 h.appendChild(document.createTextNode('We found '+D.name+' in the national registry, pulled '+D._facts+' facts about your department and county, matched your request to the right NFPA standard, and wrote all four FEMA narratives. '+blanks+' red blanks are left for facts only your officers know.'));how.appendChild(h);
 $('dout').hidden=false;
 var f=$('f');if(f){f.org.value=D.name;if(D.state)f.state.value=D.state;var map={ppe:'PPE / turnout gear',scba:'SCBA',radio:'Other equipment',equip:'Other equipment',train:'Training',well:'Wellness and fitness'};f.req.value=map[A.item];f.orgtype.value=/volunteer/i.test(D.type)?'All-volunteer':'Mostly volunteer / combination'}}
$('dcopy').addEventListener('click',function(){if(navigator.clipboard)navigator.clipboard.writeText(window.__draftText||'').then(function(){$('dcopy').textContent='Copied'});ev('draft_copy')});
$('ddl').addEventListener('click',function(){var a=document.createElement('a');a.href=URL.createObjectURL(new Blob([window.__draftText||''],{type:'text/plain'}));a.download='AFG-narratives-'+(D?D.name.replace(/[^A-Za-z0-9]+/g,'-'):'draft')+'.txt';a.click();ev('draft_copy')});
$('dres_cta').addEventListener('click',function(){ev('reserve_click')});
var fd=new URLSearchParams(location.search).get('fdid');
if(fd){getJ('/api/dept?fdid='+encodeURIComponent(fd)).then(function(j){if(j.results&&j.results.length){US=j.us;last=j.results;pick(0)}}).catch(function(){})}
})();
