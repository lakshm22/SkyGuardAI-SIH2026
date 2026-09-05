export const API_STORAGE_KEY = "skyguard.apiBase";
export const AUTH_STORAGE_KEY = "skyguard.adminToken";
const DEFAULT_API_BASE = (import.meta.env["VITE_SKYGUARD_API_URL"] as string | undefined) ?? "http://localhost:8000/api";
export type Severity = "Normal" | "Warning" | "Critical";
export interface Station { station_id:string; name:string; latitude:number; longitude:number; health:number; status:Severity; last_seen?:string|null }
export interface Reading { id:number; station_id:string; timestamp:string; temperature:number; pressure:number; humidity:number; anomaly:boolean; anomaly_score:number; confidence:number; severity:Severity; root_cause:string; explanation:string; corrected_values:{temperature:number;pressure:number;humidity:number}|null }
export interface Alert { id:number; station_id:string; timestamp:string; parameter:string; severity:Severity; score:number; status:"Active"|"Resolved"; root_cause:string; explanation:string }
export interface Dashboard { station:Pick<Station,"station_id"|"name"|"latitude"|"longitude"|"health"|"status">; latest:Reading|null; trend:Reading[]; latest_alert:Alert|null }
export interface MonitorStatus { enabled:boolean; interval_seconds:number }
export function getApiBase(){ if(typeof window==='undefined') return DEFAULT_API_BASE; return window.localStorage.getItem(API_STORAGE_KEY)||DEFAULT_API_BASE }
export function setApiBase(url:string){ if(typeof window==='undefined')return; const clean=url.trim().replace(/\/+$/,''); if(clean)window.localStorage.setItem(API_STORAGE_KEY,clean);else window.localStorage.removeItem(API_STORAGE_KEY) }
export function defaultApiBase(){return DEFAULT_API_BASE}
export function getAdminToken(){return typeof window==='undefined'?null:window.localStorage.getItem(AUTH_STORAGE_KEY)}
export function setAdminToken(token:string|null){if(typeof window!=='undefined'){if(token)window.localStorage.setItem(AUTH_STORAGE_KEY,token);else window.localStorage.removeItem(AUTH_STORAGE_KEY)}}
async function request<T>(path:string,init:RequestInit={}):Promise<T>{
 const headers=new Headers(init.headers); if(init.body)headers.set('Content-Type','application/json'); const token=getAdminToken(); if(token)headers.set('Authorization',`Bearer ${token}`);
 const res=await fetch(`${getApiBase()}${path}`,{...init,headers}); if(!res.ok)throw new Error(`${res.status} ${res.statusText}`); return await res.json() as T;
}
export const api={
 health:()=>request<{status:string;model:string}>('/health'),
 login:(username:string,password:string)=>request<{token:string;username:string}>('/auth/login',{method:'POST',body:JSON.stringify({username,password})}),
 stations:()=>request<Station[]>('/stations'),
 addStation:(payload:{station_id:string;name:string;latitude:number;longitude:number})=>request('/stations',{method:'POST',body:JSON.stringify(payload)}),
 deleteStation:(id:string)=>request(`/stations/${encodeURIComponent(id)}`,{method:'DELETE'}),
 dashboard:(id:string)=>request<Dashboard>(`/dashboard/${encodeURIComponent(id)}`),
 alerts:(limit=20)=>request<Alert[]>(`/alerts?limit=${limit}`),
 acknowledgeAlert:(id:number)=>request<Alert>(`/alerts/${id}`,{method:'PATCH',body:JSON.stringify({status:'Resolved'})}),
 simulate:(station_id:string,anomaly_type:string)=>request<unknown>('/simulate',{method:'POST',body:JSON.stringify({station_id,anomaly_type})}),
 retrain:()=>request<{message:string}>('/model/retrain',{method:'POST'}),
 monitor:()=>request<MonitorStatus>('/monitor'),
 setMonitor:(enabled:boolean,interval_seconds:number)=>request<MonitorStatus>('/monitor',{method:'POST',body:JSON.stringify({enabled,interval_seconds})}),
 downloadReport:async(stationId?:string)=>{const token=getAdminToken();const res=await fetch(`${getApiBase()}/export/report.pdf${stationId?`?station_id=${encodeURIComponent(stationId)}`:''}`,{headers:token?{Authorization:`Bearer ${token}`}:{}});if(!res.ok)throw new Error(`${res.status} ${res.statusText}`);const blob=await res.blob();const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='skyguard-anomaly-report.pdf';a.click();URL.revokeObjectURL(url)},
}
const DEMO_STATIONS:Station[]=[['AWS01','Chennai AWS-01',13.0827,80.2707,96,'Normal'],['AWS02','Coimbatore AWS-02',11.0168,76.9558,88,'Normal'],['AWS03','Madurai AWS-03',9.9252,78.1198,76,'Warning'],['AWS04','Trichy AWS-04',10.7905,78.7047,65,'Warning'],['AWS05','Ooty AWS-05',11.4102,76.695,93,'Normal'],['AWS06','Rameswaram AWS-06',9.2885,79.3129,59,'Critical']].map(([station_id,name,latitude,longitude,health,status])=>({station_id:station_id as string,name:name as string,latitude:latitude as number,longitude:longitude as number,health:health as number,status:status as Severity,last_seen:null}));
export function demoStations(){return DEMO_STATIONS}
export function demoDashboard(stationId:string):Dashboard{const station=DEMO_STATIONS.find(s=>s.station_id===stationId)||DEMO_STATIONS[0];const base=Date.now()-50*60000;const trend:Reading[]=Array.from({length:24},(_,i)=>{const w=Math.sin(i/2.3);return{id:i,station_id:station.station_id,timestamp:new Date(base+i*120000).toISOString(),temperature:Number((31.2+w*.8).toFixed(1)),pressure:Number((1007.6+w*1.4).toFixed(1)),humidity:Number((70+w*4).toFixed(0)),anomaly:false,anomaly_score:.08+Math.abs(w)*.05,confidence:.9,severity:'Normal',root_cause:'Normal operating range',explanation:'',corrected_values:null}});return{station,latest:trend[23],trend,latest_alert:station.status==='Normal'?null:{id:1,station_id:station.station_id,timestamp:new Date().toISOString(),parameter:'Temperature',severity:station.status,score:.97,status:'Active',root_cause:'Temperature sensor malfunction',explanation:'Temperature is much higher than the historical pattern and neighbouring stations.'}}}
export function demoAlerts():Alert[]{return [['Chennai AWS-01','Temperature','Critical',.97,'Active'],['Madurai AWS-03','Humidity','Warning',.62,'Resolved'],['Trichy AWS-04','Pressure','Warning',.58,'Resolved'],['Coimbatore AWS-02','Temperature','Warning',.55,'Resolved'],['Rameswaram AWS-06','Humidity','Critical',.96,'Resolved']].map(([station_id,parameter,severity,score,status],i)=>({id:i+1,station_id:station_id as string,timestamp:new Date(Date.now()-(i+1)*55*60000).toISOString(),parameter:parameter as string,severity:severity as Severity,score:score as number,status:status as 'Active'|'Resolved',root_cause:`${parameter} deviation`,explanation:''}))}
