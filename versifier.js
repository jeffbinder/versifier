forms = {
    'quatrain-iamb-tri': {
        meter: 'u-u-u-',
        repetitions: 4,
        rhyme_scheme: 'ABAB'
    },
    'couplets-iamb-pent': {
        meter: 'u-u-u-u-u-',
        repetitions: 8,
        rhyme_scheme: 'AABBCCDD'
    },
    'couplets-ana-tet': {
        meter: 'uu-uu-uu-uu-',
        repetitions: 8,
        rhyme_scheme: 'AABBCCDD'
    },
    'blank-verse': {
        meter: 'u-u-u-u-u-',
        repetitions: 8,
        rhyme_scheme: 'ABCDEFGH'
    },
    'shakes-sonnet': {
        meter: 'u-u-u-u-u-',
        repetitions: 14,
        rhyme_scheme: 'ABABCDCDEFEFGG'
    },
    'spens-stanza': {
        meter: 'u-u-u-u-u-|u-u-u-u-u-|u-u-u-u-u-|u-u-u-u-u-|u-u-u-u-u-|u-u-u-u-u-|u-u-u-u-u-|u-u-u-u-u-|u-u-u-u-u-u-',
        repetitions: 1,
        rhyme_scheme: 'ABABBCBCC'
    },
    'ottava': {
        meter: 'u-u-u-u-u-',
        repetitions: 8,
        rhyme_scheme: 'ABABABCC'
    }
};

function update_verse_form()
{
    var form = $("#verse-form").val();
    if (form == "custom") {
        return;
    }
    $("#meter").val(forms[form].meter);
    $("#repetitions").val(forms[form].repetitions);
    $("#rhyme_scheme").val(forms[form].rhyme_scheme);
}

function set_custom_verse_form()
{
    $("#verse-form").val('custom');
}

function generate()
{
    $(".versifier-output").html("Writing poem...");
    $.ajax({
        type: "GET",
        url: "/apps/versifier/versify.cgi",
        dataType: "text",
        data: {
            corpus_name: $("#corpus").val(),
            meter: $("#meter").val(),
            repetitions: $("#repetitions").val(),
            rhyme_scheme: $("#rhyme_scheme").val()
        },
        complete: function (response) {
            if (response.statusText == "OK") {
                $(".versifier-output").html(response.responseText);
            } else {
            }
        }
    });
}

$(function () {
    update_verse_form();
    $("#verse-form").change(function (e) {
        update_verse_form();
    });
    $("#meter,#repetitions,#rhyme_scheme").change(function (e) {
        set_custom_verse_form();
    });
});