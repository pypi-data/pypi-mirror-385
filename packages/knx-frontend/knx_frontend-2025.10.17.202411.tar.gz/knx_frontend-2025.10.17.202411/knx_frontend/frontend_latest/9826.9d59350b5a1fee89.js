/*! For license information please see 9826.9d59350b5a1fee89.js.LICENSE.txt */
export const __webpack_id__="9826";export const __webpack_ids__=["9826"];export const __webpack_modules__={72582:function(t,e,i){i.a(t,(async function(t,e){try{var s=i(69868),n=i(84922),a=i(11991),o=i(60434),r=i(7556),c=i(93327),h=(i(81164),i(95635),t([c]));c=(h.then?(await h)():h)[0];class l extends n.WF{render(){const t=this.icon||this.stateObj&&this.hass?.entities[this.stateObj.entity_id]?.icon||this.stateObj?.attributes.icon;if(t)return n.qy`<ha-icon .icon=${t}></ha-icon>`;if(!this.stateObj)return n.s6;if(!this.hass)return this._renderFallback();const e=(0,c.fq)(this.hass,this.stateObj,this.stateValue).then((t=>t?n.qy`<ha-icon .icon=${t}></ha-icon>`:this._renderFallback()));return n.qy`${(0,o.T)(e)}`}_renderFallback(){const t=(0,r.t)(this.stateObj);return n.qy`
      <ha-svg-icon
        .path=${c.l[t]||c.lW}
      ></ha-svg-icon>
    `}}(0,s.__decorate)([(0,a.MZ)({attribute:!1})],l.prototype,"hass",void 0),(0,s.__decorate)([(0,a.MZ)({attribute:!1})],l.prototype,"stateObj",void 0),(0,s.__decorate)([(0,a.MZ)({attribute:!1})],l.prototype,"stateValue",void 0),(0,s.__decorate)([(0,a.MZ)()],l.prototype,"icon",void 0),l=(0,s.__decorate)([(0,a.EM)("ha-state-icon")],l),e()}catch(l){e(l)}}))},88297:function(t,e,i){i.a(t,(async function(t,s){try{i.r(e),i.d(e,{KNXEntitiesView:()=>w});var n=i(69868),a=i(84922),o=i(11991),r=i(65940),c=i(92491),h=(i(49609),i(56730),i(81164),i(93672),i(72582)),l=(i(95635),i(68985)),d=i(90933),_=i(73120),y=i(47420),u=i(49432),b=i(92095),p=t([c,h]);[c,h]=p.then?(await p)():p;const $="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z",f="M11 7V9H13V7H11M14 17V15H13V11H10V13H11V15H10V17H14M22 12C22 17.5 17.5 22 12 22C6.5 22 2 17.5 2 12C2 6.5 6.5 2 12 2C17.5 2 22 6.5 22 12M20 12C20 7.58 16.42 4 12 4C7.58 4 4 7.58 4 12C4 16.42 7.58 20 12 20C16.42 20 20 16.42 20 12Z",v="M22.1 21.5L2.4 1.7L1.1 3L4.1 6C2.8 7.6 2 9.7 2 12C2 17.5 6.5 22 12 22C14.3 22 16.4 21.2 18 19.9L20.8 22.7L22.1 21.5M12 20C7.6 20 4 16.4 4 12C4 10.3 4.6 8.7 5.5 7.4L11 12.9V17H13V14.9L16.6 18.5C15.3 19.4 13.7 20 12 20M8.2 5L6.7 3.5C8.3 2.6 10.1 2 12 2C17.5 2 22 6.5 22 12C22 13.9 21.4 15.7 20.5 17.3L19 15.8C19.6 14.7 20 13.4 20 12C20 7.6 16.4 4 12 4C10.6 4 9.3 4.4 8.2 5M11 7H13V9H11V7Z",m="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",C="M14.06,9L15,9.94L5.92,19H5V18.08L14.06,9M17.66,3C17.41,3 17.15,3.1 16.96,3.29L15.13,5.12L18.88,8.87L20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18.17,3.09 17.92,3 17.66,3M14.06,6.19L3,17.25V21H6.75L17.81,9.94L14.06,6.19Z",g="M18 7C16.9 7 16 7.9 16 9V15C16 16.1 16.9 17 18 17H20C21.1 17 22 16.1 22 15V11H20V15H18V9H22V7H18M2 7V17H8V15H4V7H2M11 7C9.9 7 9 7.9 9 9V15C9 16.1 9.9 17 11 17H13C14.1 17 15 16.1 15 15V9C15 7.9 14.1 7 13 7H11M11 9H13V15H11V9Z",x=new b.Q("knx-entities-view");class w extends a.WF{firstUpdated(){this._fetchEntities()}willUpdate(){const t=new URLSearchParams(d.G.location.search);this.filterDevice=t.get("device_id")}async _fetchEntities(){(0,u.ek)(this.hass).then((t=>{x.debug(`Fetched ${t.length} entity entries.`),this.knx_entities=t.map((t=>{const e=this.hass.states[t.entity_id],i=t.device_id?this.hass.devices[t.device_id]:void 0,s=t.area_id??i?.area_id,n=s?this.hass.areas[s]:void 0;return{...t,entityState:e,friendly_name:e?.attributes.friendly_name??t.name??t.original_name??"",device_name:i?.name??"",area_name:n?.name??"",disabled:!!t.disabled_by}}))})).catch((t=>{x.error("getEntityEntries",t),(0,l.o)("/knx/error",{replace:!0,data:t})}))}render(){return this.hass&&this.knx_entities?a.qy`
      <hass-tabs-subpage-data-table
        .hass=${this.hass}
        .narrow=${this.narrow}
        .route=${this.route}
        .tabs=${this.tabs}
        .localizeFunc=${this.knx.localize}
        .columns=${this._columns(this.hass.language)}
        .data=${this.knx_entities}
        .hasFab=${!0}
        .searchLabel=${this.hass.localize("ui.components.data-table.search")}
        .clickable=${!1}
        .filter=${this.filterDevice}
      >
        <ha-fab
          slot="fab"
          .label=${this.hass.localize("ui.common.add")}
          extended
          @click=${this._entityCreate}
        >
          <ha-svg-icon slot="icon" .path=${m}></ha-svg-icon>
        </ha-fab>
      </hass-tabs-subpage-data-table>
    `:a.qy` <hass-loading-screen></hass-loading-screen> `}_entityCreate(){(0,l.o)("/knx/entities/create")}constructor(...t){super(...t),this.knx_entities=[],this.filterDevice=null,this._columns=(0,r.A)((t=>{const e="56px",i="224px";return{icon:{title:"",minWidth:e,maxWidth:e,type:"icon",template:t=>t.disabled?a.qy`<ha-svg-icon
                slot="icon"
                label="Disabled entity"
                .path=${v}
                style="color: var(--disabled-text-color);"
              ></ha-svg-icon>`:a.qy`
                <ha-state-icon
                  slot="item-icon"
                  .hass=${this.hass}
                  .stateObj=${t.entityState}
                ></ha-state-icon>
              `},friendly_name:{showNarrow:!0,filterable:!0,sortable:!0,title:"Friendly Name",flex:2},entity_id:{filterable:!0,sortable:!0,title:"Entity ID",flex:1},device_name:{filterable:!0,sortable:!0,title:"Device",flex:1},device_id:{hidden:!0,title:"Device ID",filterable:!0,template:t=>t.device_id??""},area_name:{title:"Area",sortable:!0,filterable:!0,flex:1},actions:{showNarrow:!0,title:"",minWidth:i,maxWidth:i,type:"icon-button",template:t=>a.qy`
          <ha-icon-button
            .label=${"More info"}
            .path=${f}
            .entityEntry=${t}
            @click=${this._entityMoreInfo}
          ></ha-icon-button>
          <ha-icon-button
            .label=${this.hass.localize("ui.common.edit")}
            .path=${C}
            .entityEntry=${t}
            @click=${this._entityEdit}
          ></ha-icon-button>
          <ha-icon-button
            .label=${this.knx.localize("entities_view_monitor_telegrams")}
            .path=${g}
            .entityEntry=${t}
            @click=${this._showEntityTelegrams}
          ></ha-icon-button>
          <ha-icon-button
            .label=${this.hass.localize("ui.common.delete")}
            .path=${$}
            .entityEntry=${t}
            @click=${this._entityDelete}
          ></ha-icon-button>
        `}}})),this._entityEdit=t=>{t.stopPropagation();const e=t.target.entityEntry;(0,l.o)("/knx/entities/edit/"+e.entity_id)},this._entityMoreInfo=t=>{t.stopPropagation();const e=t.target.entityEntry;(0,_.r)(d.G.document.querySelector("home-assistant"),"hass-more-info",{entityId:e.entity_id})},this._showEntityTelegrams=async t=>{t.stopPropagation();const e=t.target?.entityEntry;if(!e)return x.error("No entity entry found in event target"),void(0,l.o)("/knx/group_monitor");try{const t=(await(0,u.wE)(this.hass,e.entity_id)).data.knx,i=Object.values(t).flatMap((t=>{if("object"!=typeof t||null===t)return[];const{write:e,state:i,passive:s}=t;return[e,i,...Array.isArray(s)?s:[]]})).filter((t=>Boolean(t))),s=[...new Set(i)];if(s.length>0){const t=s.join(",");(0,l.o)(`/knx/group_monitor?destination=${encodeURIComponent(t)}`)}else x.warn("No group addresses found for entity",e.entity_id),(0,l.o)("/knx/group_monitor")}catch(i){x.error("Failed to load entity configuration for monitor",e.entity_id,i),(0,l.o)("/knx/group_monitor")}},this._entityDelete=t=>{t.stopPropagation();const e=t.target.entityEntry;(0,y.dk)(this,{text:`${this.hass.localize("ui.common.delete")} ${e.entity_id}?`}).then((t=>{t&&(0,u.$b)(this.hass,e.entity_id).then((()=>{x.debug("entity deleted",e.entity_id),this._fetchEntities()})).catch((t=>{(0,y.K$)(this,{title:"Deletion failed",text:t})}))}))}}}w.styles=a.AH`
    hass-loading-screen {
      --app-header-background-color: var(--sidebar-background-color);
      --app-header-text-color: var(--sidebar-text-color);
    }
  `,(0,n.__decorate)([(0,o.MZ)({type:Object})],w.prototype,"hass",void 0),(0,n.__decorate)([(0,o.MZ)({attribute:!1})],w.prototype,"knx",void 0),(0,n.__decorate)([(0,o.MZ)({type:Boolean,reflect:!0})],w.prototype,"narrow",void 0),(0,n.__decorate)([(0,o.MZ)({type:Object})],w.prototype,"route",void 0),(0,n.__decorate)([(0,o.MZ)({type:Array,reflect:!1})],w.prototype,"tabs",void 0),(0,n.__decorate)([(0,o.wk)()],w.prototype,"knx_entities",void 0),(0,n.__decorate)([(0,o.wk)()],w.prototype,"filterDevice",void 0),w=(0,n.__decorate)([(0,o.EM)("knx-entities-view")],w),s()}catch($){s($)}}))},60434:function(t,e,i){i.d(e,{T:()=>_});var s=i(11681),n=i(67851),a=i(40594);class o{disconnect(){this.G=void 0}reconnect(t){this.G=t}deref(){return this.G}constructor(t){this.G=t}}class r{get(){return this.Y}pause(){this.Y??=new Promise((t=>this.Z=t))}resume(){this.Z?.(),this.Y=this.Z=void 0}constructor(){this.Y=void 0,this.Z=void 0}}var c=i(64363);const h=t=>!(0,n.sO)(t)&&"function"==typeof t.then,l=1073741823;class d extends a.Kq{render(...t){return t.find((t=>!h(t)))??s.c0}update(t,e){const i=this._$Cbt;let n=i.length;this._$Cbt=e;const a=this._$CK,o=this._$CX;this.isConnected||this.disconnected();for(let s=0;s<e.length&&!(s>this._$Cwt);s++){const t=e[s];if(!h(t))return this._$Cwt=s,t;s<n&&t===i[s]||(this._$Cwt=l,n=0,Promise.resolve(t).then((async e=>{for(;o.get();)await o.get();const i=a.deref();if(void 0!==i){const s=i._$Cbt.indexOf(t);s>-1&&s<i._$Cwt&&(i._$Cwt=s,i.setValue(e))}})))}return s.c0}disconnected(){this._$CK.disconnect(),this._$CX.pause()}reconnected(){this._$CK.reconnect(this),this._$CX.resume()}constructor(){super(...arguments),this._$Cwt=l,this._$Cbt=[],this._$CK=new o(this),this._$CX=new r}}const _=(0,c.u$)(d)}};
//# sourceMappingURL=9826.9d59350b5a1fee89.js.map