(function(){var i=document.getElementById('w'),r=document.getElementById('wr');if(!i)return;
i.addEventListener('input',function(){var v=parseFloat(i.value.replace(',','.'));if(!(v>=0))return;r.textContent=i.dataset.t.replace('{n}',Math.round(v*parseFloat(i.dataset.k)/100))});})();
