"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["5413"],{75518:function(e,t,a){a(35748),a(65315),a(22416),a(37089),a(12977),a(5934),a(95013);var r=a(69868),o=a(84922),i=a(11991),s=a(21431),n=a(73120);a(23749),a(57674);let l,c,h,d,p,u,m,_,b,g=e=>e;const v={boolean:()=>a.e("2436").then(a.bind(a,33999)),constant:()=>a.e("3668").then(a.bind(a,33855)),float:()=>a.e("742").then(a.bind(a,84053)),grid:()=>a.e("7828").then(a.bind(a,57311)),expandable:()=>a.e("364").then(a.bind(a,51079)),integer:()=>a.e("7346").then(a.bind(a,40681)),multi_select:()=>Promise.all([a.e("6216"),a.e("3706")]).then(a.bind(a,99681)),positive_time_period_dict:()=>a.e("3540").then(a.bind(a,87551)),select:()=>a.e("2500").then(a.bind(a,10079)),string:()=>a.e("3627").then(a.bind(a,10070)),optional_actions:()=>a.e("3044").then(a.bind(a,96943))},y=(e,t)=>e?!t.name||t.flatten?e:e[t.name]:null;class $ extends o.WF{getFormProperties(){return{}}async focus(){await this.updateComplete;const e=this.renderRoot.querySelector(".root");if(e)for(const t of e.children)if("HA-ALERT"!==t.tagName){t instanceof o.mN&&await t.updateComplete,t.focus();break}}willUpdate(e){e.has("schema")&&this.schema&&this.schema.forEach((e=>{var t;"selector"in e||null===(t=v[e.type])||void 0===t||t.call(v)}))}render(){return(0,o.qy)(l||(l=g`
      <div class="root" part="root">
        ${0}
        ${0}
      </div>
    `),this.error&&this.error.base?(0,o.qy)(c||(c=g`
              <ha-alert alert-type="error">
                ${0}
              </ha-alert>
            `),this._computeError(this.error.base,this.schema)):"",this.schema.map((e=>{var t;const a=((e,t)=>e&&t.name?e[t.name]:null)(this.error,e),r=((e,t)=>e&&t.name?e[t.name]:null)(this.warning,e);return(0,o.qy)(h||(h=g`
            ${0}
            ${0}
          `),a?(0,o.qy)(d||(d=g`
                  <ha-alert own-margin alert-type="error">
                    ${0}
                  </ha-alert>
                `),this._computeError(a,e)):r?(0,o.qy)(p||(p=g`
                    <ha-alert own-margin alert-type="warning">
                      ${0}
                    </ha-alert>
                  `),this._computeWarning(r,e)):"","selector"in e?(0,o.qy)(u||(u=g`<ha-selector
                  .schema=${0}
                  .hass=${0}
                  .narrow=${0}
                  .name=${0}
                  .selector=${0}
                  .value=${0}
                  .label=${0}
                  .disabled=${0}
                  .placeholder=${0}
                  .helper=${0}
                  .localizeValue=${0}
                  .required=${0}
                  .context=${0}
                ></ha-selector>`),e,this.hass,this.narrow,e.name,e.selector,y(this.data,e),this._computeLabel(e,this.data),e.disabled||this.disabled||!1,e.required?"":e.default,this._computeHelper(e),this.localizeValue,e.required||!1,this._generateContext(e)):(0,s._)(this.fieldElementName(e.type),Object.assign({schema:e,data:y(this.data,e),label:this._computeLabel(e,this.data),helper:this._computeHelper(e),disabled:this.disabled||e.disabled||!1,hass:this.hass,localize:null===(t=this.hass)||void 0===t?void 0:t.localize,computeLabel:this.computeLabel,computeHelper:this.computeHelper,localizeValue:this.localizeValue,context:this._generateContext(e)},this.getFormProperties())))})))}fieldElementName(e){return`ha-form-${e}`}_generateContext(e){if(!e.context)return;const t={};for(const[a,r]of Object.entries(e.context))t[a]=this.data[r];return t}createRenderRoot(){const e=super.createRenderRoot();return this.addValueChangedListener(e),e}addValueChangedListener(e){e.addEventListener("value-changed",(e=>{e.stopPropagation();const t=e.target.schema;if(e.target===this)return;const a=!t.name||"flatten"in t&&t.flatten?e.detail.value:{[t.name]:e.detail.value};this.data=Object.assign(Object.assign({},this.data),a),(0,n.r)(this,"value-changed",{value:this.data})}))}_computeLabel(e,t){return this.computeLabel?this.computeLabel(e,t):e?e.name:""}_computeHelper(e){return this.computeHelper?this.computeHelper(e):""}_computeError(e,t){return Array.isArray(e)?(0,o.qy)(m||(m=g`<ul>
        ${0}
      </ul>`),e.map((e=>(0,o.qy)(_||(_=g`<li>
              ${0}
            </li>`),this.computeError?this.computeError(e,t):e)))):this.computeError?this.computeError(e,t):e}_computeWarning(e,t){return this.computeWarning?this.computeWarning(e,t):e}constructor(...e){super(...e),this.narrow=!1,this.disabled=!1}}$.styles=(0,o.AH)(b||(b=g`
    .root > * {
      display: block;
    }
    .root > *:not([own-margin]):not(:last-child) {
      margin-bottom: 24px;
    }
    ha-alert[own-margin] {
      margin-bottom: 4px;
    }
  `)),(0,r.__decorate)([(0,i.MZ)({attribute:!1})],$.prototype,"hass",void 0),(0,r.__decorate)([(0,i.MZ)({type:Boolean})],$.prototype,"narrow",void 0),(0,r.__decorate)([(0,i.MZ)({attribute:!1})],$.prototype,"data",void 0),(0,r.__decorate)([(0,i.MZ)({attribute:!1})],$.prototype,"schema",void 0),(0,r.__decorate)([(0,i.MZ)({attribute:!1})],$.prototype,"error",void 0),(0,r.__decorate)([(0,i.MZ)({attribute:!1})],$.prototype,"warning",void 0),(0,r.__decorate)([(0,i.MZ)({type:Boolean})],$.prototype,"disabled",void 0),(0,r.__decorate)([(0,i.MZ)({attribute:!1})],$.prototype,"computeError",void 0),(0,r.__decorate)([(0,i.MZ)({attribute:!1})],$.prototype,"computeWarning",void 0),(0,r.__decorate)([(0,i.MZ)({attribute:!1})],$.prototype,"computeLabel",void 0),(0,r.__decorate)([(0,i.MZ)({attribute:!1})],$.prototype,"computeHelper",void 0),(0,r.__decorate)([(0,i.MZ)({attribute:!1})],$.prototype,"localizeValue",void 0),$=(0,r.__decorate)([(0,i.EM)("ha-form")],$)},42612:function(e,t,a){a.a(e,(async function(e,r){try{a.r(t),a.d(t,{DialogForm:function(){return _}});a(35748),a(5934),a(95013);var o=a(69868),i=a(84922),s=a(11991),n=a(73120),l=a(76943),c=a(72847),h=(a(75518),a(83566)),d=e([l]);l=(d.then?(await d)():d)[0];let p,u,m=e=>e;class _ extends i.WF{async showDialog(e){this._params=e,this._data=e.data||{}}closeDialog(){return this._params=void 0,this._data={},(0,n.r)(this,"dialog-closed",{dialog:this.localName}),!0}_submit(){var e,t;null===(e=this._params)||void 0===e||null===(t=e.submit)||void 0===t||t.call(e,this._data),this.closeDialog()}_cancel(){var e,t;null===(e=this._params)||void 0===e||null===(t=e.cancel)||void 0===t||t.call(e),this.closeDialog()}_valueChanged(e){this._data=e.detail.value}render(){return this._params&&this.hass?(0,i.qy)(p||(p=m`
      <ha-dialog
        open
        scrimClickAction
        escapeKeyAction
        .heading=${0}
        @closed=${0}
      >
        <ha-form
          dialogInitialFocus
          .hass=${0}
          .computeLabel=${0}
          .computeHelper=${0}
          .data=${0}
          .schema=${0}
          @value-changed=${0}
        >
        </ha-form>
        <ha-button
          appearance="plain"
          @click=${0}
          slot="secondaryAction"
        >
          ${0}
        </ha-button>
        <ha-button @click=${0} slot="primaryAction">
          ${0}
        </ha-button>
      </ha-dialog>
    `),(0,c.l)(this.hass,this._params.title),this._cancel,this.hass,this._params.computeLabel,this._params.computeHelper,this._data,this._params.schema,this._valueChanged,this._cancel,this._params.cancelText||this.hass.localize("ui.common.cancel"),this._submit,this._params.submitText||this.hass.localize("ui.common.save")):i.s6}constructor(...e){super(...e),this._data={}}}_.styles=[h.nA,(0,i.AH)(u||(u=m``))],(0,o.__decorate)([(0,s.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,o.__decorate)([(0,s.wk)()],_.prototype,"_params",void 0),(0,o.__decorate)([(0,s.wk)()],_.prototype,"_data",void 0),_=(0,o.__decorate)([(0,s.EM)("dialog-form")],_),r()}catch(p){r(p)}}))}}]);
//# sourceMappingURL=5413.31d7e23fedcdc0aa.js.map