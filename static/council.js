/*
Javascript file for Council-Insights application.
Uses jQuery which is loaded via the Google CDN through base.html template.
*/

$(document).ready(function(){

    // Displays highlights if any exist
    {% for highlight in agenda.highlights.all %}
        $( "div:contains('{{ agenda.agenda_text|hl_slice:highlight }}')" ).css( "background-color: #FFFF00" );
    {% endfor %}
  
  });