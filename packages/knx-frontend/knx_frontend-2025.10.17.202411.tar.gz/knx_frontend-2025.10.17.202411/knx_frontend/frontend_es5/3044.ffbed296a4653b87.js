"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["3044"],{96943:function(t,e,a){a.a(t,(async function(t,i){try{a.r(e),a.d(e,{HaFormOptionalActions:function(){return f}});a(79827),a(35748),a(65315),a(837),a(37089),a(5934),a(18223),a(95013);var o=a(69868),s=a(84922),d=a(11991),n=a(65940),c=a(20674),l=a(76943),h=(a(25223),a(95635),a(75518),t([l]));l=(h.then?(await h)():h)[0];let r,p,u,m,_,y=t=>t;const b="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",v=[];class f extends s.WF{async focus(){var t;await this.updateComplete,null===(t=this.renderRoot.querySelector("ha-form"))||void 0===t||t.focus()}updated(t){if(super.updated(t),t.has("data")){var e;const t=null!==(e=this._displayActions)&&void 0!==e?e:v,a=this._hiddenActions(this.schema.schema,t);this._displayActions=[...t,...a.filter((t=>t in this.data))]}}render(){var t,e,a;const i=null!==(t=this._displayActions)&&void 0!==t?t:v,o=this._displaySchema(this.schema.schema,null!==(e=this._displayActions)&&void 0!==e?e:[]),d=this._hiddenActions(this.schema.schema,i),n=new Map(this.computeLabel?this.schema.schema.map((t=>[t.name,t])):[]);return(0,s.qy)(r||(r=y`
      ${0}
      ${0}
    `),o.length>0?(0,s.qy)(p||(p=y`
            <ha-form
              .hass=${0}
              .data=${0}
              .schema=${0}
              .disabled=${0}
              .computeLabel=${0}
              .computeHelper=${0}
              .localizeValue=${0}
            ></ha-form>
          `),this.hass,this.data,o,this.disabled,this.computeLabel,this.computeHelper,this.localizeValue):s.s6,d.length>0?(0,s.qy)(u||(u=y`
            <ha-button-menu
              @action=${0}
              fixed
              @closed=${0}
            >
              <ha-button slot="trigger" appearance="filled" size="small">
                <ha-svg-icon .path=${0} slot="start"></ha-svg-icon>
                ${0}
              </ha-button>
              ${0}
            </ha-button-menu>
          `),this._handleAddAction,c.d,b,(null===(a=this.localize)||void 0===a?void 0:a.call(this,"ui.components.form-optional-actions.add"))||"Add interaction",d.map((t=>{const e=n.get(t);return(0,s.qy)(m||(m=y`
                  <ha-list-item>
                    ${0}
                  </ha-list-item>
                `),this.computeLabel&&e?this.computeLabel(e):t)}))):s.s6)}_handleAddAction(t){var e,a;const i=this._hiddenActions(this.schema.schema,null!==(e=this._displayActions)&&void 0!==e?e:v)[t.detail.index];this._displayActions=[...null!==(a=this._displayActions)&&void 0!==a?a:[],i]}constructor(...t){super(...t),this.disabled=!1,this._hiddenActions=(0,n.A)(((t,e)=>t.map((t=>t.name)).filter((t=>!e.includes(t))))),this._displaySchema=(0,n.A)(((t,e)=>t.filter((t=>e.includes(t.name)))))}}f.styles=(0,s.AH)(_||(_=y`
    :host {
      display: flex !important;
      flex-direction: column;
      gap: 24px;
    }
    :host ha-form {
      display: block;
    }
  `)),(0,o.__decorate)([(0,d.MZ)({attribute:!1})],f.prototype,"localize",void 0),(0,o.__decorate)([(0,d.MZ)({attribute:!1})],f.prototype,"hass",void 0),(0,o.__decorate)([(0,d.MZ)({attribute:!1})],f.prototype,"data",void 0),(0,o.__decorate)([(0,d.MZ)({attribute:!1})],f.prototype,"schema",void 0),(0,o.__decorate)([(0,d.MZ)({type:Boolean})],f.prototype,"disabled",void 0),(0,o.__decorate)([(0,d.MZ)({attribute:!1})],f.prototype,"computeLabel",void 0),(0,o.__decorate)([(0,d.MZ)({attribute:!1})],f.prototype,"computeHelper",void 0),(0,o.__decorate)([(0,d.MZ)({attribute:!1})],f.prototype,"localizeValue",void 0),(0,o.__decorate)([(0,d.wk)()],f.prototype,"_displayActions",void 0),f=(0,o.__decorate)([(0,d.EM)("ha-form-optional_actions")],f),i()}catch(r){i(r)}}))}}]);
//# sourceMappingURL=3044.ffbed296a4653b87.js.map