"use strict";
/* Local-only configuration importer. No external APIs, telemetry, or HTML injection. */
(() => {
  const fileInput=document.getElementById("theme-import-file");
  const status=document.getElementById("theme-import-status");
  if(!fileInput||!status)return;
  const cards=["lifetime","languages","activity","ranking","heatmap","emblem"];
  const tokens=["background","surface","outline","text","muted","accent","success"];
  const names=new Set(["theme","timezone","output","colors","cards","layout","size",
    "language_rows","typography","show_rank_stars","show_card_subtitles"]);
  const validHex=v=>typeof v==="string"&&/^#[0-9a-fA-F]{6}$/.test(v);
  function check(value) {
    if(!value||typeof value!=="object"||Array.isArray(value))
      throw Error("O conteúdo deve ser um objeto JSON.");
    if(Object.keys(value).some(k=>!names.has(k)))throw Error("Campo desconhecido no JSON.");
    const theme=value.theme??"midnight";
    if(!["midnight","graphite","aurora"].includes(theme))throw Error("Tema inválido.");
    const color=value.colors??{};
    if(!color||typeof color!=="object"||Array.isArray(color)||
       Object.entries(color).some(([k,v])=>!tokens.includes(k)||!validHex(v)))
      throw Error("As cores devem usar tokens conhecidos e formato #RRGGBB.");
    const selected=value.cards??cards;
    if(!Array.isArray(selected)||selected.length<1||selected.length>6||
       selected.some(v=>typeof v!=="string"||!cards.includes(v))||
       new Set(selected).size!==selected.length)throw Error("Seleção de cards inválida.");
    const layout=value.layout??"stacked",size=value.size??"standard";
    if(!["stacked","paired"].includes(layout)||!["compact","standard","large"].includes(size))
      throw Error("Layout ou tamanho inválido.");
    const languageRows=value.language_rows??10, typography=value.typography??"standard";
    if(![5,8,10].includes(languageRows)||!["compact","standard","large"].includes(typography))
      throw Error("Densidade ou tipografia inválida.");
    const stars=value.show_rank_stars??true, subtitles=value.show_card_subtitles??true;
    if(typeof stars!=="boolean"||typeof subtitles!=="boolean")
      throw Error("Opções de estrelas e subtítulos devem ser booleanas.");
    const output=value.output??"assets/axr-stats";
    if(typeof output!=="string"||!output||output.length>200||output.startsWith("/")||
      output.includes("\\")||/[\x00-\x1f]/.test(output)||
      output.split("/").some(p=>!p||p==="."||p===".."||[".git",".github"].includes(p.toLowerCase())))
      throw Error("Pasta de saída inválida.");
    const timezone=value.timezone??"UTC";
    if(typeof timezone!=="string"||!timezone||timezone.length>100)
      throw Error("Fuso horário inválido.");
    try{new Intl.DateTimeFormat("en-US",{timeZone:timezone});}
    catch{throw Error("Fuso horário não reconhecido.");}
    return {theme,color,selected,layout,size,languageRows,typography,stars,subtitles,output,timezone};
  }
  function update(node,eventType="change"){node.dispatchEvent(new Event(eventType,{bubbles:true}));}
  function apply(cfg) {
    const theme=document.querySelector('[data-theme="'+cfg.theme+'"]');
    theme.click();
    for(const [key,value] of Object.entries(cfg.color)){
      const hex=document.querySelector('[data-hex="'+key+'"]');
      hex.value=value.toUpperCase();update(hex,"input");
    }
    for(const id of cards){
      const checkbox=document.querySelector('[data-include-card="'+id+'"]');
      checkbox.checked=cfg.selected.includes(id);
    }
    const values={
      "theme-layout":cfg.layout,"theme-size":cfg.size,
      "theme-language-rows":String(cfg.languageRows),"theme-typography":cfg.typography,
      "theme-output-dir":cfg.output,"theme-timezone":cfg.timezone
    };
    for(const [id,value] of Object.entries(values))document.getElementById(id).value=value;
    document.getElementById("theme-rank-stars").checked=cfg.stars;
    document.getElementById("theme-card-subtitles").checked=cfg.subtitles;
    if(Object.keys(cfg.color).length)document.getElementById("theme-color-details").open=true;
    update(document.getElementById("theme-layout")); // redraw all settings in one pass
  }
  fileInput.addEventListener("change",async()=>{
    const file=fileInput.files?.[0];
    if(!file)return;
    try{
      if(file.size>64000)throw Error("O JSON deve ter até 64 KB.");
      const cfg=check(JSON.parse(await file.text()));
      apply(cfg);
      status.textContent="Configuração importada e validada. Confira a prévia.";
    }catch(error){
      status.textContent="Importação recusada: "+
        (error instanceof SyntaxError?"JSON malformado.":error.message);
    }finally{fileInput.value="";}
  });
})();
