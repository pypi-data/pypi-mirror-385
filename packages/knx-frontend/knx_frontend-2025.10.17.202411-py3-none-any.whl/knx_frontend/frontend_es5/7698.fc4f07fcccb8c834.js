/*! For license information please see 7698.fc4f07fcccb8c834.js.LICENSE.txt */
"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["7698"],{12024:function(e,t,a){a.d(t,{K:function(){return s},t:function(){return l}});var n=a(84922);let r,i,o=e=>e;const s=(0,n.qy)(r||(r=o`<svg height="24" viewBox="0 0 24 24" width="24"><path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"></path></svg>`)),l=(0,n.qy)(i||(i=o`<svg height="24" viewBox="0 0 24 24" width="24"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"></path></svg>`))},34795:function(e,t,a){a.a(e,(async function(e,t){try{var n=a(43318),r=a(21721),i=a(68824),o=e([n,r]);[n,r]=o.then?(await o)():o,(0,i.U)(n.$4,r.t),t()}catch(s){t(s)}}))},84545:function(e,t,a){a.d(t,{WA:function(){return c},mm:function(){return u}});var n=a(84922);let r,i,o,s,l,d=e=>e;const c=(0,n.AH)(r||(r=d`
button {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;

  position: relative;
  display: block;
  margin: 0;
  padding: 0;
  background: none; /** NOTE: IE11 fix */
  color: inherit;
  border: none;
  font: inherit;
  text-align: left;
  text-transform: inherit;
  -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
}
`)),u=((0,n.AH)(i||(i=d`
a {
  -webkit-tap-highlight-color: rgba(0, 0, 0, 0);

  position: relative;
  display: inline-block;
  background: initial;
  color: inherit;
  font: inherit;
  text-transform: inherit;
  text-decoration: none;
  outline: none;
}
a:focus,
a:focus.page-selected {
  text-decoration: underline;
}
`)),(0,n.AH)(o||(o=d`
svg {
  display: block;
  min-width: var(--svg-icon-min-width, 24px);
  min-height: var(--svg-icon-min-height, 24px);
  fill: var(--svg-icon-fill, currentColor);
  pointer-events: none;
}
`)),(0,n.AH)(s||(s=d`[hidden] { display: none !important; }`)),(0,n.AH)(l||(l=d`
:host {
  display: block;

  /* --app-datepicker-width: 300px; */
  /* --app-datepicker-primary-color: #4285f4; */
  /* --app-datepicker-header-height: 80px; */
}

* {
  box-sizing: border-box;
}
`)))},43318:function(e,t,a){a.a(e,(async function(e,n){try{a.d(t,{$4:function(){return f},$g:function(){return u},B0:function(){return o},Gf:function(){return d},YB:function(){return p},eB:function(){return c},tn:function(){return h}});a(35748),a(88238),a(34536),a(16257),a(20152),a(44711),a(72108),a(77030),a(95013);var r=a(96904),i=e([r]);r=(i.then?(await i)():i)[0];const o=Intl&&Intl.DateTimeFormat,s=[38,33,36],l=[40,34,35],d=new Set([37,...s]),c=new Set([39,...l]),u=new Set([39,...s]),h=new Set([37,...l]),p=new Set([37,39,...s,...l]),f="app-datepicker";n()}catch(o){n(o)}}))},21721:function(e,t,a){a.a(e,(async function(e,n){try{a.d(t,{t:function(){return G}});a(35748),a(65315),a(37089),a(5934),a(88238),a(34536),a(16257),a(20152),a(44711),a(72108),a(77030),a(95013);var r=a(69868),i=a(84922),o=a(11991),s=a(60602),l=a(75907),d=a(33055),c=a(30010),u=a(12024),h=a(84545),p=a(43318),f=a(46091),y=a(8406),m=a(48742),_=a(11489),b=a(11558),w=a(30961),v=a(84812),g=a(68991),k=a(44113),D=a(14580),x=a(50691),T=a(26753),S=a(18697),C=a(39311),F=a(93044),M=a(21870),$=a(13417),U=a(15399),N=a(6603),W=e([p,y,k,w]);[p,y,k,w]=W.then?(await W)():W;let L,E,Y,O,V,q,A,P,Z,B,z,H,K,I,j,J,R=e=>e;class G extends i.WF{get startView(){return this._startView}set startView(e){const t=e||"calendar";if("calendar"!==t&&"yearList"!==t)return;const a=this._startView;this._startView=t,this.requestUpdate("startView",a)}get min(){return this._hasMin?(0,M.h)(this._min):""}set min(e){const t=(0,g.t)(e),a=(0,x.v)(e,t);this._min=a?t:this._todayDate,this._hasMin=a,this.requestUpdate("min")}get max(){return this._hasMax?(0,M.h)(this._max):""}set max(e){const t=(0,g.t)(e),a=(0,x.v)(e,t);this._max=a?t:this._maxDate,this._hasMax=a,this.requestUpdate("max")}get value(){return(0,M.h)(this._focusedDate)}set value(e){const t=(0,g.t)(e),a=(0,x.v)(e,t)?t:this._todayDate;this._focusedDate=new Date(a),this._selectedDate=this._lastSelectedDate=new Date(a)}disconnectedCallback(){super.disconnectedCallback(),this._tracker&&(this._tracker.disconnect(),this._tracker=void 0)}render(){this._formatters.locale!==this.locale&&(this._formatters=(0,w.G)(this.locale));const e="yearList"===this._startView?this._renderDatepickerYearList():this._renderDatepickerCalendar(),t=this.inline?null:(0,i.qy)(L||(L=R`<div class="datepicker-header" part="header">${0}</div>`),this._renderHeaderSelectorButton());return(0,i.qy)(E||(E=R`
    ${0}
    <div class="datepicker-body" part="body">${0}</div>
    `),t,(0,s.P)(e))}firstUpdated(){let e;e="calendar"===this._startView?this.inline?this.shadowRoot.querySelector(".btn__month-selector"):this._buttonSelectorYear:this._yearViewListItem,(0,m.w)(this,"datepicker-first-updated",{firstFocusableElement:e,value:this.value})}async updated(e){const t=this._startView;if(e.has("min")||e.has("max")){this._yearList=(0,$.N)(this._min,this._max),"yearList"===t&&this.requestUpdate();const e=+this._min,a=+this._max;if((0,b.u)(e,a)>864e5){const t=+this._focusedDate;let n=t;t<e&&(n=e),t>a&&(n=a),this.value=(0,M.h)(new Date(n))}}if(e.has("_startView")||e.has("startView")){if("yearList"===t){const e=48*(this._selectedDate.getUTCFullYear()-this._min.getUTCFullYear()-2);(0,F.G)(this._yearViewFullList,{top:e,left:0})}if("calendar"===t&&null==this._tracker){const e=this.calendarsContainer;let t=!1,a=!1,n=!1;if(e){const r={down:()=>{n||(t=!0,this._dx=0)},move:(r,i)=>{if(n||!t)return;const o=this._dx,s=o<0&&(0,D.n)(e,"has-max-date")||o>0&&(0,D.n)(e,"has-min-date");!s&&Math.abs(o)>0&&t&&(a=!0,e.style.transform=`translateX(${(0,T.b)(o)}px)`),this._dx=s?0:o+(r.x-i.x)},up:async(r,i,o)=>{if(t&&a){const r=this._dx,i=e.getBoundingClientRect().width/3,o=Math.abs(r)>Number(this.dragRatio)*i,s=350,l="cubic-bezier(0, 0, .4, 1)",d=o?(0,T.b)(i*(r<0?-1:1)):0;n=!0,await(0,f.K)(e,{hasNativeWebAnimation:this._hasNativeWebAnimation,keyframes:[{transform:`translateX(${r}px)`},{transform:`translateX(${d}px)`}],options:{duration:s,easing:l}}),o&&this._updateMonth(r<0?"next":"previous").handleEvent(),t=a=n=!1,this._dx=-1/0,e.removeAttribute("style"),(0,m.w)(this,"datepicker-animation-finished")}else t&&(this._updateFocusedDate(o),t=a=!1,this._dx=-1/0)}};this._tracker=new N.J(e,r)}}e.get("_startView")&&"calendar"===t&&this._focusElement('[part="year-selector"]')}this._updatingDateWithKey&&(this._focusElement('[part="calendars"]:nth-of-type(2) .day--focused'),this._updatingDateWithKey=!1)}_focusElement(e){const t=this.shadowRoot.querySelector(e);t&&t.focus()}_renderHeaderSelectorButton(){const{yearFormat:e,dateFormat:t}=this._formatters,a="calendar"===this.startView,n=this._focusedDate,r=t(n),o=e(n);return(0,i.qy)(Y||(Y=R`
    <button
      class="${0}"
      type="button"
      part="year-selector"
      data-view="${0}"
      @click="${0}">${0}</button>

    <div class="datepicker-toolbar" part="toolbar">
      <button
        class="${0}"
        type="button"
        part="calendar-selector"
        data-view="${0}"
        @click="${0}">${0}</button>
    </div>
    `),(0,l.H)({"btn__year-selector":!0,selected:!a}),"yearList",this._updateView("yearList"),o,(0,l.H)({"btn__calendar-selector":!0,selected:a}),"calendar",this._updateView("calendar"),r)}_renderDatepickerYearList(){const{yearFormat:e}=this._formatters,t=this._focusedDate.getUTCFullYear();return(0,i.qy)(O||(O=R`
    <div class="datepicker-body__year-list-view" part="year-list-view">
      <div class="year-list-view__full-list" part="year-list" @click="${0}">
      ${0}</div>
    </div>
    `),this._updateYear,this._yearList.map((a=>(0,i.qy)(V||(V=R`<button
        class="${0}"
        type="button"
        part="year"
        .year="${0}">${0}</button>`),(0,l.H)({"year-list-view__list-item":!0,"year--selected":t===a}),a,e((0,c.m)(a,0,1))))))}_renderDatepickerCalendar(){const{longMonthYearFormat:e,dayFormat:t,fullDateFormat:a,longWeekdayFormat:n,narrowWeekdayFormat:r}=this._formatters,o=(0,C.S)(this.disabledDays,Number),s=(0,C.S)(this.disabledDates,g.t),c=this.showWeekNumber,h=this._focusedDate,p=this.firstDayOfWeek,f=(0,g.t)(),m=this._selectedDate,_=this._max,b=this._min,{calendars:w,disabledDaysSet:k,disabledDatesSet:D,weekdays:x}=(0,v.n)({dayFormat:t,fullDateFormat:a,longWeekdayFormat:n,narrowWeekdayFormat:r,firstDayOfWeek:p,disabledDays:o,disabledDates:s,locale:this.locale,selectedDate:m,showWeekNumber:this.showWeekNumber,weekNumberType:this.weekNumberType,max:_,min:b,weekLabel:this.weekLabel}),T=!w[0].calendar.length,S=!w[2].calendar.length,F=x.map((e=>(0,i.qy)(q||(q=R`<th
        class="calendar-weekday"
        part="calendar-weekday"
        role="columnheader"
        aria-label="${0}"
      >
        <div class="weekday" part="weekday">${0}</div>
      </th>`),e.label,e.value))),M=(0,d.u)(w,(e=>e.key),(({calendar:t},a)=>{if(!t.length)return(0,i.qy)(A||(A=R`<div class="calendar-container" part="calendar"></div>`));const n=`calendarcaption${a}`,r=t[1][1].fullDate,o=1===a,s=o&&!this._isInVisibleMonth(h,m)?(0,y.Y)({disabledDaysSet:k,disabledDatesSet:D,hasAltKey:!1,keyCode:36,focusedDate:h,selectedDate:m,minTime:+b,maxTime:+_}):h;return(0,i.qy)(P||(P=R`
      <div class="calendar-container" part="calendar">
        <table class="calendar-table" part="table" role="grid" aria-labelledby="${0}">
          <caption id="${0}">
            <div class="calendar-label" part="label">${0}</div>
          </caption>

          <thead role="rowgroup">
            <tr class="calendar-weekdays" part="weekdays" role="row">${0}</tr>
          </thead>

          <tbody role="rowgroup">${0}</tbody>
        </table>
      </div>
      `),n,n,r?e(r):"",F,t.map((e=>(0,i.qy)(Z||(Z=R`<tr role="row">${0}</tr>`),e.map(((e,t)=>{const{disabled:a,fullDate:n,label:r,value:d}=e;if(!n&&d&&c&&t<1)return(0,i.qy)(B||(B=R`<th
                      class="full-calendar__day weekday-label"
                      part="calendar-day"
                      scope="row"
                      role="rowheader"
                      abbr="${0}"
                      aria-label="${0}"
                    >${0}</th>`),r,r,d);if(!d||!n)return(0,i.qy)(z||(z=R`<td class="full-calendar__day day--empty" part="calendar-day"></td>`));const u=+new Date(n),p=+h===u,y=o&&s.getUTCDate()===Number(d);return(0,i.qy)(H||(H=R`
                  <td
                    tabindex="${0}"
                    class="${0}"
                    part="calendar-day${0}"
                    role="gridcell"
                    aria-disabled="${0}"
                    aria-label="${0}"
                    aria-selected="${0}"
                    .fullDate="${0}"
                    .day="${0}"
                  >
                    <div
                      class="calendar-day"
                      part="day${0}"
                    >${0}</div>
                  </td>
                  `),y?"0":"-1",(0,l.H)({"full-calendar__day":!0,"day--disabled":a,"day--today":+f===u,"day--focused":!a&&p}),+f===u?" calendar-today":"",a?"true":"false",r,p?"true":"false",n,d,+f===u?" today":"",d)}))))))}));return this._disabledDatesSet=D,this._disabledDaysSet=k,(0,i.qy)(K||(K=R`
    <div class="datepicker-body__calendar-view" part="calendar-view">
      <div class="calendar-view__month-selector" part="month-selectors">
        <div class="month-selector-container">${0}</div>

        <div class="month-selector-container">${0}</div>
      </div>

      <div
        class="${0}"
        part="calendars"
        @keyup="${0}"
      >${0}</div>
    </div>
    `),T?null:(0,i.qy)(I||(I=R`
          <button
            class="btn__month-selector"
            type="button"
            part="month-selector"
            aria-label="Previous month"
            @click="${0}"
          >${0}</button>
        `),this._updateMonth("previous"),u.K),S?null:(0,i.qy)(j||(j=R`
          <button
            class="btn__month-selector"
            type="button"
            part="month-selector"
            aria-label="Next month"
            @click="${0}"
          >${0}</button>
        `),this._updateMonth("next"),u.t),(0,l.H)({"calendars-container":!0,"has-min-date":T,"has-max-date":S}),this._updateFocusedDateWithKeyboard,M)}_updateView(e){return(0,S.c)((()=>{"calendar"===e&&(this._selectedDate=this._lastSelectedDate=new Date((0,U.V)(this._focusedDate,this._min,this._max))),this._startView=e}))}_updateMonth(e){return(0,S.c)((()=>{if(null==this.calendarsContainer)return this.updateComplete;const t=this._lastSelectedDate||this._selectedDate,a=this._min,n=this._max,r="previous"===e,i=(0,c.m)(t.getUTCFullYear(),t.getUTCMonth()+(r?-1:1),1),o=i.getUTCFullYear(),s=i.getUTCMonth(),l=a.getUTCFullYear(),d=a.getUTCMonth(),u=n.getUTCFullYear(),h=n.getUTCMonth();return o<l||o<=l&&s<d||(o>u||o>=u&&s>h)||(this._lastSelectedDate=i,this._selectedDate=this._lastSelectedDate),this.updateComplete}))}_updateYear(e){const t=(0,_.z)(e,(e=>(0,D.n)(e,"year-list-view__list-item")));if(null==t)return;const a=(0,U.V)(new Date(this._focusedDate).setUTCFullYear(+t.year),this._min,this._max);this._selectedDate=this._lastSelectedDate=new Date(a),this._focusedDate=new Date(a),this._startView="calendar"}_updateFocusedDate(e){const t=(0,_.z)(e,(e=>(0,D.n)(e,"full-calendar__day")));null==t||["day--empty","day--disabled","day--focused","weekday-label"].some((e=>(0,D.n)(t,e)))||(this._focusedDate=new Date(t.fullDate),(0,m.w)(this,"datepicker-value-updated",{isKeypress:!1,value:this.value}))}_updateFocusedDateWithKeyboard(e){const t=e.keyCode;if(13===t||32===t)return(0,m.w)(this,"datepicker-value-updated",{keyCode:t,isKeypress:!0,value:this.value}),void(this._focusedDate=new Date(this._selectedDate));if(9===t||!p.YB.has(t))return;const a=this._selectedDate,n=(0,y.Y)({keyCode:t,selectedDate:a,disabledDatesSet:this._disabledDatesSet,disabledDaysSet:this._disabledDaysSet,focusedDate:this._focusedDate,hasAltKey:e.altKey,maxTime:+this._max,minTime:+this._min});this._isInVisibleMonth(n,a)||(this._selectedDate=this._lastSelectedDate=n),this._focusedDate=n,this._updatingDateWithKey=!0,(0,m.w)(this,"datepicker-value-updated",{keyCode:t,isKeypress:!0,value:this.value})}_isInVisibleMonth(e,t){const a=e.getUTCFullYear(),n=e.getUTCMonth(),r=t.getUTCFullYear(),i=t.getUTCMonth();return a===r&&n===i}get calendarsContainer(){return this.shadowRoot.querySelector(".calendars-container")}constructor(){super(),this.firstDayOfWeek=0,this.showWeekNumber=!1,this.weekNumberType="first-4-day-week",this.landscape=!1,this.locale=(0,k.f)(),this.disabledDays="",this.disabledDates="",this.weekLabel="Wk",this.inline=!1,this.dragRatio=.15,this._hasMin=!1,this._hasMax=!1,this._disabledDaysSet=new Set,this._disabledDatesSet=new Set,this._dx=-1/0,this._hasNativeWebAnimation="animate"in HTMLElement.prototype,this._updatingDateWithKey=!1;const e=(0,g.t)(),t=(0,w.G)(this.locale),a=(0,M.h)(e),n=(0,g.t)("2100-12-31");this.value=a,this.startView="calendar",this._min=new Date(e),this._max=new Date(n),this._todayDate=e,this._maxDate=n,this._yearList=(0,$.N)(e,n),this._selectedDate=new Date(e),this._focusedDate=new Date(e),this._formatters=t}}G.styles=[h.mm,h.WA,(0,i.AH)(J||(J=R`
    :host {
      width: 312px;
      /** NOTE: Magic number as 16:9 aspect ratio does not look good */
      /* height: calc((var(--app-datepicker-width) / .66) - var(--app-datepicker-footer-height, 56px)); */
      background-color: var(--app-datepicker-bg-color, #fff);
      color: var(--app-datepicker-color, #000);
      border-radius:
        var(--app-datepicker-border-top-left-radius, 0)
        var(--app-datepicker-border-top-right-radius, 0)
        var(--app-datepicker-border-bottom-right-radius, 0)
        var(--app-datepicker-border-bottom-left-radius, 0);
      contain: content;
      overflow: hidden;
    }
    :host([landscape]) {
      display: flex;

      /** <iphone-5-landscape-width> - <standard-side-margin-width> */
      min-width: calc(568px - 16px * 2);
      width: calc(568px - 16px * 2);
    }

    .datepicker-header + .datepicker-body {
      border-top: 1px solid var(--app-datepicker-separator-color, #ddd);
    }
    :host([landscape]) > .datepicker-header + .datepicker-body {
      border-top: none;
      border-left: 1px solid var(--app-datepicker-separator-color, #ddd);
    }

    .datepicker-header {
      display: flex;
      flex-direction: column;
      align-items: flex-start;

      position: relative;
      padding: 16px 24px;
    }
    :host([landscape]) > .datepicker-header {
      /** :this.<one-liner-month-day-width> + :this.<side-padding-width> */
      min-width: calc(14ch + 24px * 2);
    }

    .btn__year-selector,
    .btn__calendar-selector {
      color: var(--app-datepicker-selector-color, rgba(0, 0, 0, .55));
      cursor: pointer;
      /* outline: none; */
    }
    .btn__year-selector.selected,
    .btn__calendar-selector.selected {
      color: currentColor;
    }

    /**
      * NOTE: IE11-only fix. This prevents formatted focused date from overflowing the container.
      */
    .datepicker-toolbar {
      width: 100%;
    }

    .btn__year-selector {
      font-size: 16px;
      font-weight: 700;
    }
    .btn__calendar-selector {
      font-size: 36px;
      font-weight: 700;
      line-height: 1;
    }

    .datepicker-body {
      position: relative;
      width: 100%;
      overflow: hidden;
    }

    .datepicker-body__calendar-view {
      min-height: 56px;
    }

    .calendar-view__month-selector {
      display: flex;
      align-items: center;

      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      padding: 0 8px;
      z-index: 1;
    }

    .month-selector-container {
      max-height: 56px;
      height: 100%;
    }
    .month-selector-container + .month-selector-container {
      margin: 0 0 0 auto;
    }

    .btn__month-selector {
      padding: calc((56px - 24px) / 2);
      /**
        * NOTE: button element contains no text, only SVG.
        * No extra height will incur with such setting.
        */
      line-height: 0;
    }
    .btn__month-selector > svg {
      fill: currentColor;
    }

    .calendars-container {
      display: flex;
      justify-content: center;

      position: relative;
      top: 0;
      left: calc(-100%);
      width: calc(100% * 3);
      transform: translateZ(0);
      will-change: transform;
      /**
        * NOTE: Required for Pointer Events API to work on touch devices.
        * Native \`pan-y\` action will be fired by the browsers since we only care about the
        * horizontal direction. This is great as vertical scrolling still works even when touch
        * event happens on a datepicker's calendar.
        */
      touch-action: pan-y;
      /* outline: none; */
    }

    .year-list-view__full-list {
      max-height: calc(48px * 7);
      overflow-y: auto;

      scrollbar-color: var(--app-datepicker-scrollbar-thumb-bg-color, rgba(0, 0, 0, .35)) rgba(0, 0, 0, 0);
      scrollbar-width: thin;
    }
    .year-list-view__full-list::-webkit-scrollbar {
      width: 8px;
      background-color: rgba(0, 0, 0, 0);
    }
    .year-list-view__full-list::-webkit-scrollbar-thumb {
      background-color: var(--app-datepicker-scrollbar-thumb-bg-color, rgba(0, 0, 0, .35));
      border-radius: 50px;
    }
    .year-list-view__full-list::-webkit-scrollbar-thumb:hover {
      background-color: var(--app-datepicker-scrollbar-thumb-hover-bg-color, rgba(0, 0, 0, .5));
    }

    .calendar-weekdays > th,
    .weekday-label {
      color: var(--app-datepicker-weekday-color, rgba(0, 0, 0, .55));
      font-weight: 400;
      transform: translateZ(0);
      will-change: transform;
    }

    .calendar-container,
    .calendar-label,
    .calendar-table {
      width: 100%;
    }

    .calendar-container {
      position: relative;
      padding: 0 16px 16px;
    }

    .calendar-table {
      -moz-user-select: none;
      -webkit-user-select: none;
      user-select: none;

      border-collapse: collapse;
      border-spacing: 0;
      text-align: center;
    }

    .calendar-label {
      display: flex;
      align-items: center;
      justify-content: center;

      height: 56px;
      font-weight: 500;
      text-align: center;
    }

    .calendar-weekday,
    .full-calendar__day {
      position: relative;
      width: calc(100% / 7);
      height: 0;
      padding: calc(100% / 7 / 2) 0;
      outline: none;
      text-align: center;
    }
    .full-calendar__day:not(.day--disabled):focus {
      outline: #000 dotted 1px;
      outline: -webkit-focus-ring-color auto 1px;
    }
    :host([showweeknumber]) .calendar-weekday,
    :host([showweeknumber]) .full-calendar__day {
      width: calc(100% / 8);
      padding-top: calc(100% / 8);
      padding-bottom: 0;
    }
    :host([showweeknumber]) th.weekday-label {
      padding: 0;
    }

    /**
      * NOTE: Interesting fact! That is ::after will trigger paint when dragging. This will trigger
      * layout and paint on **ONLY** affected nodes. This is much cheaper as compared to rendering
      * all :::after of all calendar day elements. When dragging the entire calendar container,
      * because of all layout and paint trigger on each and every ::after, this becomes a expensive
      * task for the browsers especially on low-end devices. Even though animating opacity is much
      * cheaper, the technique does not work here. Adding 'will-change' will further reduce overall
      * painting at the expense of memory consumption as many cells in a table has been promoted
      * a its own layer.
      */
    .full-calendar__day:not(.day--empty):not(.day--disabled):not(.weekday-label) {
      transform: translateZ(0);
      will-change: transform;
    }
    .full-calendar__day:not(.day--empty):not(.day--disabled):not(.weekday-label).day--focused::after,
    .full-calendar__day:not(.day--empty):not(.day--disabled):not(.day--focused):not(.weekday-label):hover::after {
      content: '';
      display: block;
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: var(--app-datepicker-accent-color, #1a73e8);
      border-radius: 50%;
      opacity: 0;
      pointer-events: none;
    }
    .full-calendar__day:not(.day--empty):not(.day--disabled):not(.weekday-label) {
      cursor: pointer;
      pointer-events: auto;
      -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
    }
    .full-calendar__day.day--focused:not(.day--empty):not(.day--disabled):not(.weekday-label)::after,
    .full-calendar__day.day--today.day--focused:not(.day--empty):not(.day--disabled):not(.weekday-label)::after {
      opacity: 1;
    }

    .calendar-weekday > .weekday,
    .full-calendar__day > .calendar-day {
      display: flex;
      align-items: center;
      justify-content: center;

      position: absolute;
      top: 5%;
      left: 5%;
      width: 90%;
      height: 90%;
      color: currentColor;
      font-size: 14px;
      pointer-events: none;
      z-index: 1;
    }
    .full-calendar__day.day--today {
      color: var(--app-datepicker-accent-color, #1a73e8);
    }
    .full-calendar__day.day--focused,
    .full-calendar__day.day--today.day--focused {
      color: var(--app-datepicker-focused-day-color, #fff);
    }
    .full-calendar__day.day--empty,
    .full-calendar__day.weekday-label,
    .full-calendar__day.day--disabled > .calendar-day {
      pointer-events: none;
    }
    .full-calendar__day.day--disabled:not(.day--today) {
      color: var(--app-datepicker-disabled-day-color, rgba(0, 0, 0, .55));
    }

    .year-list-view__list-item {
      position: relative;
      width: 100%;
      padding: 12px 16px;
      text-align: center;
      /** NOTE: Reduce paint when hovering and scrolling, but this increases memory usage */
      /* will-change: opacity; */
      /* outline: none; */
    }
    .year-list-view__list-item::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: var(--app-datepicker-focused-year-bg-color, #000);
      opacity: 0;
      pointer-events: none;
    }
    .year-list-view__list-item:focus::after {
      opacity: .05;
    }
    .year-list-view__list-item.year--selected {
      color: var(--app-datepicker-accent-color, #1a73e8);
      font-size: 24px;
      font-weight: 500;
    }

    @media (any-hover: hover) {
      .btn__month-selector:hover,
      .year-list-view__list-item:hover {
        cursor: pointer;
      }
      .full-calendar__day:not(.day--empty):not(.day--disabled):not(.day--focused):not(.weekday-label):hover::after {
        opacity: .15;
      }
      .year-list-view__list-item:hover::after {
        opacity: .05;
      }
    }

    @supports (background: -webkit-canvas(squares)) {
      .calendar-container {
        padding: 56px 16px 16px;
      }

      table > caption {
        position: absolute;
        top: 0;
        left: 50%;
        transform: translate3d(-50%, 0, 0);
        will-change: transform;
      }
    }
    `))],(0,r.__decorate)([(0,o.MZ)({type:Number,reflect:!0})],G.prototype,"firstDayOfWeek",void 0),(0,r.__decorate)([(0,o.MZ)({type:Boolean,reflect:!0})],G.prototype,"showWeekNumber",void 0),(0,r.__decorate)([(0,o.MZ)({type:String,reflect:!0})],G.prototype,"weekNumberType",void 0),(0,r.__decorate)([(0,o.MZ)({type:Boolean,reflect:!0})],G.prototype,"landscape",void 0),(0,r.__decorate)([(0,o.MZ)({type:String,reflect:!0})],G.prototype,"startView",null),(0,r.__decorate)([(0,o.MZ)({type:String,reflect:!0})],G.prototype,"min",null),(0,r.__decorate)([(0,o.MZ)({type:String,reflect:!0})],G.prototype,"max",null),(0,r.__decorate)([(0,o.MZ)({type:String})],G.prototype,"value",null),(0,r.__decorate)([(0,o.MZ)({type:String})],G.prototype,"locale",void 0),(0,r.__decorate)([(0,o.MZ)({type:String})],G.prototype,"disabledDays",void 0),(0,r.__decorate)([(0,o.MZ)({type:String})],G.prototype,"disabledDates",void 0),(0,r.__decorate)([(0,o.MZ)({type:String})],G.prototype,"weekLabel",void 0),(0,r.__decorate)([(0,o.MZ)({type:Boolean})],G.prototype,"inline",void 0),(0,r.__decorate)([(0,o.MZ)({type:Number})],G.prototype,"dragRatio",void 0),(0,r.__decorate)([(0,o.MZ)({type:Date,attribute:!1})],G.prototype,"_selectedDate",void 0),(0,r.__decorate)([(0,o.MZ)({type:Date,attribute:!1})],G.prototype,"_focusedDate",void 0),(0,r.__decorate)([(0,o.MZ)({type:String,attribute:!1})],G.prototype,"_startView",void 0),(0,r.__decorate)([(0,o.P)(".year-list-view__full-list")],G.prototype,"_yearViewFullList",void 0),(0,r.__decorate)([(0,o.P)(".btn__year-selector")],G.prototype,"_buttonSelectorYear",void 0),(0,r.__decorate)([(0,o.P)(".year-list-view__list-item")],G.prototype,"_yearViewListItem",void 0),(0,r.__decorate)([(0,o.Ls)({passive:!0})],G.prototype,"_updateYear",null),(0,r.__decorate)([(0,o.Ls)({passive:!0})],G.prototype,"_updateFocusedDateWithKeyboard",null),n()}catch(L){n(L)}}))},46091:function(e,t,a){a.d(t,{K:function(){return n}});a(35748),a(65315),a(22416),a(5934),a(95013);async function n(e,t){const{hasNativeWebAnimation:a=!1,keyframes:n=[],options:r={duration:100}}=t||{};if(Array.isArray(n)&&n.length)return new Promise((t=>{if(a){e.animate(n,r).onfinish=()=>t()}else{const[,a]=n||[],i=()=>{e.removeEventListener("transitionend",i),t()};e.addEventListener("transitionend",i),e.style.transitionDuration=`${r.duration}ms`,r.easing&&(e.style.transitionTimingFunction=r.easing),Object.keys(a).forEach((t=>{t&&(e.style[t]=a[t])}))}}))}},8406:function(e,t,a){a.a(e,(async function(e,n){try{a.d(t,{Y:function(){return d}});var r=a(30010),i=a(43318),o=a(58375),s=e([i,o]);function d({hasAltKey:e,keyCode:t,focusedDate:a,selectedDate:n,disabledDaysSet:s,disabledDatesSet:l,minTime:d,maxTime:c}){const u=a.getUTCFullYear(),h=a.getUTCMonth(),p=a.getUTCDate(),f=+a,y=n.getUTCFullYear(),m=n.getUTCMonth();let _=u,b=h,w=p,v=!0;switch((m!==h||y!==u)&&(_=y,b=m,w=1,v=34===t||33===t||35===t),v){case f===d&&i.Gf.has(t):case f===c&&i.eB.has(t):break;case 38===t:w-=7;break;case 40===t:w+=7;break;case 37===t:w-=1;break;case 39===t:w+=1;break;case 34===t:e?_+=1:b+=1;break;case 33===t:e?_-=1:b-=1;break;case 35===t:b+=1,w=0;break;default:w=1}if(34===t||33===t){const e=(0,r.m)(_,b+1,0).getUTCDate();w>e&&(w=e)}return(0,o.i)({keyCode:t,maxTime:c,minTime:d,disabledDaysSet:s,disabledDatesSet:l,focusedDate:(0,r.m)(_,b,w)})}[i,o]=s.then?(await s)():s,n()}catch(l){n(l)}}))},68824:function(e,t,a){function n(e,t){window.customElements&&!window.customElements.get(e)&&window.customElements.define(e,t)}a.d(t,{U:function(){return n}})},48742:function(e,t,a){function n(e,t,a){return e.dispatchEvent(new CustomEvent(t,{detail:a,bubbles:!0,composed:!0}))}a.d(t,{w:function(){return n}})},11489:function(e,t,a){a.d(t,{z:function(){return n}});a(65315),a(84136);function n(e,t){return e.composedPath().find((e=>e instanceof HTMLElement&&t(e)))}},11558:function(e,t,a){function n(e,t){return+t-+e}a.d(t,{u:function(){return n}})},30961:function(e,t,a){a.a(e,(async function(e,n){try{a.d(t,{G:function(){return l}});var r=a(75660),i=a(43318),o=e([i]);function l(e){const t=(0,i.B0)(e,{timeZone:"UTC",weekday:"short",month:"short",day:"numeric"}),a=(0,i.B0)(e,{timeZone:"UTC",day:"numeric"}),n=(0,i.B0)(e,{timeZone:"UTC",year:"numeric",month:"short",day:"numeric"}),o=(0,i.B0)(e,{timeZone:"UTC",year:"numeric",month:"long"}),s=(0,i.B0)(e,{timeZone:"UTC",weekday:"long"}),l=(0,i.B0)(e,{timeZone:"UTC",weekday:"narrow"}),d=(0,i.B0)(e,{timeZone:"UTC",year:"numeric"});return{locale:e,dateFormat:(0,r.f)(t),dayFormat:(0,r.f)(a),fullDateFormat:(0,r.f)(n),longMonthYearFormat:(0,r.f)(o),longWeekdayFormat:(0,r.f)(s),narrowWeekdayFormat:(0,r.f)(l),yearFormat:(0,r.f)(d)}}i=(o.then?(await o)():o)[0],n()}catch(s){n(s)}}))},84812:function(e,t,a){a.d(t,{n:function(){return d}});var n=a(52012),r=(a(35748),a(99342),a(12977),a(88238),a(34536),a(16257),a(20152),a(44711),a(72108),a(77030),a(95013),a(9724),a(65315),a(48169),a(30010));a(37089);function i(e,t){const a=function(e,t){const a=t.getUTCFullYear(),n=t.getUTCMonth(),i=t.getUTCDate(),o=t.getUTCDay();let s=o;return"first-4-day-week"===e&&(s=3),"first-day-of-year"===e&&(s=6),"first-full-week"===e&&(s=0),(0,r.m)(a,n,i-o+s)}(e,t),n=(0,r.m)(a.getUTCFullYear(),0,1),i=1+(+a-+n)/864e5;return Math.ceil(i/7)}function o(e){if(e>=0&&e<7)return Math.abs(e);return((e<0?7*Math.ceil(Math.abs(e)):0)+e)%7}function s(e,t,a){const n=o(e-t);return a?1+n:n}a(75660);const l=["disabledDatesSet","disabledDaysSet"];function d(e){const{dayFormat:t,fullDateFormat:a,locale:d,longWeekdayFormat:c,narrowWeekdayFormat:u,selectedDate:h,disabledDates:p,disabledDays:f,firstDayOfWeek:y,max:m,min:_,showWeekNumber:b,weekLabel:w,weekNumberType:v}=e,g=null==_?Number.MIN_SAFE_INTEGER:+_,k=null==m?Number.MAX_SAFE_INTEGER:+m,D=function(e){const{firstDayOfWeek:t=0,showWeekNumber:a=!1,weekLabel:n,longWeekdayFormat:i,narrowWeekdayFormat:o}=e||{},s=1+(t+(t<0?7:0))%7,l=n||"Wk",d=a?[{label:"Wk"===l?"Week":l,value:l}]:[];return Array.from(Array(7)).reduce(((e,t,a)=>{const n=(0,r.m)(2017,0,s+a);return e.push({label:i(n),value:o(n)}),e}),d)}({longWeekdayFormat:c,narrowWeekdayFormat:u,firstDayOfWeek:y,showWeekNumber:b,weekLabel:w}),x=e=>[d,e.toJSON(),null==p?void 0:p.join("_"),null==f?void 0:f.join("_"),y,null==m?void 0:m.toJSON(),null==_?void 0:_.toJSON(),b,w,v].filter(Boolean).join(":"),T=h.getUTCFullYear(),S=h.getUTCMonth(),C=[-1,0,1].map((e=>{const n=(0,r.m)(T,S+e,1),l=+(0,r.m)(T,S+e+1,0),c=x(n);if(l<g||+n>k)return{key:c,calendar:[],disabledDatesSet:new Set,disabledDaysSet:new Set};const u=function(e){const{date:t,dayFormat:a,disabledDates:n=[],disabledDays:l=[],firstDayOfWeek:d=0,fullDateFormat:c,locale:u="en-US",max:h,min:p,showWeekNumber:f=!1,weekLabel:y="Week",weekNumberType:m="first-4-day-week"}=e||{},_=o(d),b=t.getUTCFullYear(),w=t.getUTCMonth(),v=(0,r.m)(b,w,1),g=new Set(l.map((e=>s(e,_,f)))),k=new Set(n.map((e=>+e))),D=[v.toJSON(),_,u,null==h?"":h.toJSON(),null==p?"":p.toJSON(),Array.from(g).join(","),Array.from(k).join(","),m].filter(Boolean).join(":"),x=s(v.getUTCDay(),_,f),T=null==p?+new Date("2000-01-01"):+p,S=null==h?+new Date("2100-12-31"):+h,C=f?8:7,F=(0,r.m)(b,1+w,0).getUTCDate(),M=[];let $=[],U=!1,N=1;for(const o of[0,1,2,3,4,5]){for(const e of[0,1,2,3,4,5,6].concat(7===C?[]:[7])){const t=e+o*C;if(!U&&f&&0===e){const e=o<1?_:0,t=i(m,(0,r.m)(b,w,N-e)),a=`${y} ${t}`;$.push({fullDate:null,label:a,value:`${t}`,key:`${D}:${a}`,disabled:!0});continue}if(U||t<x){$.push({fullDate:null,label:"",value:"",key:`${D}:${t}`,disabled:!0});continue}const n=(0,r.m)(b,w,N),s=+n,l=g.has(e)||k.has(s)||s<T||s>S;l&&k.add(s),$.push({fullDate:n,label:c(n),value:a(n),key:`${D}:${n.toJSON()}`,disabled:l}),N+=1,N>F&&(U=!0)}M.push($),$=[]}return{disabledDatesSet:k,calendar:M,disabledDaysSet:new Set(l.map((e=>o(e)))),key:D}}({dayFormat:t,fullDateFormat:a,locale:d,disabledDates:p,disabledDays:f,firstDayOfWeek:y,max:m,min:_,showWeekNumber:b,weekLabel:w,weekNumberType:v,date:n});return Object.assign(Object.assign({},u),{},{key:c})})),F=[],M=new Set,$=new Set;for(const r of C){const{disabledDatesSet:e,disabledDaysSet:t}=r,a=(0,n.A)(r,l);if(a.calendar.length>0){if(t.size>0)for(const e of t)$.add(e);if(e.size>0)for(const t of e)M.add(t)}F.push(a)}return{calendars:F,weekdays:D,disabledDatesSet:M,disabledDaysSet:$,key:x(h)}}},68991:function(e,t,a){a.d(t,{t:function(){return r}});a(67579),a(41190);var n=a(30010);function r(e){const t=null==e?new Date:new Date(e),a="string"==typeof e&&(/^\d{4}-\d{2}-\d{2}$/i.test(e)||/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}(Z|\+00:00|-00:00)$/i.test(e)),r="number"==typeof e&&e>0&&isFinite(e);let i=t.getFullYear(),o=t.getMonth(),s=t.getDate();return(a||r)&&(i=t.getUTCFullYear(),o=t.getUTCMonth(),s=t.getUTCDate()),(0,n.m)(i,o,s)}},44113:function(e,t,a){a.a(e,(async function(e,n){try{a.d(t,{f:function(){return s}});var r=a(43318),i=e([r]);function s(){return r.B0&&(0,r.B0)().resolvedOptions&&(0,r.B0)().resolvedOptions().locale||"en-US"}r=(i.then?(await i)():i)[0],n()}catch(o){n(o)}}))},58375:function(e,t,a){a.a(e,(async function(e,n){try{a.d(t,{i:function(){return d}});var r=a(30010),i=a(43318),o=a(11558),s=e([i]);function d({keyCode:e,disabledDaysSet:t,disabledDatesSet:a,focusedDate:n,maxTime:s,minTime:l}){const d=+n;let c=d<l,u=d>s;if((0,o.u)(l,s)<864e5)return n;let h=c||u||t.has(n.getUTCDay())||a.has(d);if(!h)return n;let p=0,f=c===u?n:new Date(c?l-864e5:864e5+s);const y=f.getUTCFullYear(),m=f.getUTCMonth();let _=f.getUTCDate();for(;h;)(c||!u&&i.$g.has(e))&&(_+=1),(u||!c&&i.tn.has(e))&&(_-=1),f=(0,r.m)(y,m,_),p=+f,c||(c=p<l,c&&(f=new Date(l),p=+f,_=f.getUTCDate())),u||(u=p>s,u&&(f=new Date(s),p=+f,_=f.getUTCDate())),h=t.has(f.getUTCDay())||a.has(p);return f}i=(s.then?(await s)():s)[0],n()}catch(l){n(l)}}))},14580:function(e,t,a){function n(e,t){return e.classList.contains(t)}a.d(t,{n:function(){return n}})},50691:function(e,t,a){function n(e,t){return!(null==e||!(t instanceof Date)||isNaN(+t))}a.d(t,{v:function(){return n}})},26753:function(e,t,a){a.d(t,{b:function(){return n}});a(92344);function n(e){return e-Math.floor(e)>0?+e.toFixed(3):e}},18697:function(e,t,a){function n(e){return{passive:!0,handleEvent:e}}a.d(t,{c:function(){return n}})},39311:function(e,t,a){a.d(t,{S:function(){return n}});a(65315),a(37089),a(67579),a(91844);function n(e,t){const a="string"==typeof e&&e.length>0?e.split(/,\s*/i):[];return a.length?"function"==typeof t?a.map(t):a:[]}},93044:function(e,t,a){function n(e,t){if(null==e.scrollTo){const{top:a,left:n}=t||{};e.scrollTop=a||0,e.scrollLeft=n||0}else e.scrollTo(t)}a.d(t,{G:function(){return n}})},21870:function(e,t,a){a.d(t,{h:function(){return n}});a(67579),a(30500);function n(e){if(e instanceof Date&&!isNaN(+e)){const t=e.toJSON();return null==t?"":t.replace(/^(.+)T.+/i,"$1")}return""}},13417:function(e,t,a){a.d(t,{N:function(){return r}});var n=a(11558);function r(e,t){if((0,n.u)(e,t)<864e5)return[];const a=e.getUTCFullYear();return Array.from(Array(t.getUTCFullYear()-a+1),((e,t)=>t+a))}},15399:function(e,t,a){function n(e,t,a){const n="number"==typeof e?e:+e,r=+t,i=+a;return n<r?r:n>i?i:e}a.d(t,{V:function(){return n}})},6603:function(e,t,a){a.d(t,{J:function(){return s}});a(65315),a(84136);var n=a(33928);function r(e){const{clientX:t,clientY:a,pageX:n,pageY:r}=e,i=Math.max(n,t),o=Math.max(r,a),s=e.identifier||e.pointerId;return{x:i,y:o,id:null==s?0:s}}function i(e,t){const a=t.changedTouches;if(null==a)return{newPointer:r(t),oldPointer:e};const n=Array.from(a,(e=>r(e)));return{newPointer:null==e?n[0]:n.find((t=>t.id===e.id)),oldPointer:e}}function o(e,t,a){e.addEventListener(t,a,!!n.QQ&&{passive:!0})}class s{disconnect(){const e=this._element;e&&e.removeEventListener&&(e.removeEventListener("mousedown",this._down),e.removeEventListener("touchstart",this._down),e.removeEventListener("touchmove",this._move),e.removeEventListener("touchend",this._up))}_onDown(e){return t=>{t instanceof MouseEvent&&(this._element.addEventListener("mousemove",this._move),this._element.addEventListener("mouseup",this._up),this._element.addEventListener("mouseleave",this._up));const{newPointer:a}=i(this._startPointer,t);e(a,t),this._startPointer=a}}_onMove(e){return t=>{this._updatePointers(e,t)}}_onUp(e){return t=>{this._updatePointers(e,t,!0)}}_updatePointers(e,t,a){a&&t instanceof MouseEvent&&(this._element.removeEventListener("mousemove",this._move),this._element.removeEventListener("mouseup",this._up),this._element.removeEventListener("mouseleave",this._up));const{newPointer:n,oldPointer:r}=i(this._startPointer,t);e(n,r,t),this._startPointer=a?null:n}constructor(e,t){this._element=e,this._startPointer=null;const{down:a,move:n,up:r}=t;this._down=this._onDown(a),this._move=this._onMove(n),this._up=this._onUp(r),e&&e.addEventListener&&(e.addEventListener("mousedown",this._down),o(e,"touchstart",this._down),o(e,"touchmove",this._move),o(e,"touchend",this._up))}}},6223:function(e,t,a){a.d(t,{q:function(){return r}});let n={};function r(){return n}},90298:function(e,t,a){a.d(t,{x:function(){return r}});a(65315),a(84136),a(37089);var n=a(67874);function r(e,...t){const a=n.w.bind(null,e||t.find((e=>"object"==typeof e)));return t.map(a)}},27554:function(e,t,a){a.d(t,{Cg:function(){return i},_P:function(){return s},my:function(){return n},s0:function(){return o},w4:function(){return r}});Math.pow(10,8);const n=6048e5,r=864e5,i=6e4,o=36e5,s=Symbol.for("constructDateFrom")},67874:function(e,t,a){a.d(t,{w:function(){return r}});var n=a(27554);function r(e,t){return"function"==typeof e?e(t):e&&"object"==typeof e&&n._P in e?e[n._P](t):e instanceof Date?new e.constructor(t):new Date(t)}},59922:function(e,t,a){a.d(t,{m:function(){return l}});a(35748),a(95013);var n=a(19490);function r(e){const t=(0,n.a)(e),a=new Date(Date.UTC(t.getFullYear(),t.getMonth(),t.getDate(),t.getHours(),t.getMinutes(),t.getSeconds(),t.getMilliseconds()));return a.setUTCFullYear(t.getFullYear()),+e-+a}var i=a(90298),o=a(27554),s=a(70162);function l(e,t,a){const[n,l]=(0,i.x)(null==a?void 0:a.in,e,t),d=(0,s.o)(n),c=(0,s.o)(l),u=+d-r(d),h=+c-r(c);return Math.round((u-h)/o.w4)}},70162:function(e,t,a){a.d(t,{o:function(){return r}});var n=a(19490);function r(e,t){const a=(0,n.a)(e,null==t?void 0:t.in);return a.setHours(0,0,0,0),a}},88258:function(e,t,a){a.d(t,{k:function(){return i}});var n=a(6223),r=a(19490);function i(e,t){var a,i,o,s,l,d;const c=(0,n.q)(),u=null!==(a=null!==(i=null!==(o=null!==(s=null==t?void 0:t.weekStartsOn)&&void 0!==s?s:null==t||null===(l=t.locale)||void 0===l||null===(l=l.options)||void 0===l?void 0:l.weekStartsOn)&&void 0!==o?o:c.weekStartsOn)&&void 0!==i?i:null===(d=c.locale)||void 0===d||null===(d=d.options)||void 0===d?void 0:d.weekStartsOn)&&void 0!==a?a:0,h=(0,r.a)(e,null==t?void 0:t.in),p=h.getDay(),f=(p<u?7:0)+p-u;return h.setDate(h.getDate()-f),h.setHours(0,0,0,0),h}},19490:function(e,t,a){a.d(t,{a:function(){return r}});var n=a(67874);function r(e,t){return(0,n.w)(t||e,e)}},60602:function(e,t,a){a.d(t,{P:function(){return s}});a(35748),a(66168),a(95013);var n=a(11681),r=a(64363),i=a(67851);const o=e=>(0,i.ps)(e)?e._$litType$.h:e.strings,s=(0,r.u$)(class extends r.WL{render(e){return[e]}update(e,[t]){const a=(0,i.qb)(this.it)?o(this.it):null,r=(0,i.qb)(t)?o(t):null;if(null!==a&&(null===r||a!==r)){const t=(0,i.cN)(e).pop();let r=this.et.get(a);if(void 0===r){const e=document.createDocumentFragment();r=(0,n.XX)(n.s6,e),r.setConnected(!1),this.et.set(a,r)}(0,i.mY)(r,[t]),(0,i.Dx)(r,void 0,t)}if(null!==r){if(null===a||a!==r){const t=this.et.get(r);if(void 0!==t){const a=(0,i.cN)(t).pop();(0,i.Jz)(e),(0,i.Dx)(e,void 0,a),(0,i.mY)(e,[a])}}this.it=t}else this.it=void 0;return this.render(t)}constructor(e){super(e),this.et=new WeakMap}})},75660:function(e,t,a){a.d(t,{f:function(){return n}});a(67579),a(30500);function n(e){return t=>e.format(t).replace(/\u200e/gi,"")}},30010:function(e,t,a){function n(e,t,a){return new Date(Date.UTC(e,t,a))}a.d(t,{m:function(){return n}})}}]);
//# sourceMappingURL=7698.fc4f07fcccb8c834.js.map