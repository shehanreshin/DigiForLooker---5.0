const popup = document.getElementById('popup-container2');
const hidePopup = () => {
  popup.style.display = 'none';
};
setTimeout(hidePopup, 5000);

var secondCells = document.querySelectorAll('.current-hash-table tbody td:nth-child(5)');
var popupContainer = document.getElementById('popup-container');
var popupText = document.getElementById('popup-text');
var timeoutId;

secondCells.forEach(function (cell) {
  cell.addEventListener('mouseenter', function () {
    timeoutId = setTimeout(async function () {
      var text = cell.textContent;
      try {
        var response = await getDescriptionFromFlask(text);
        popupText.textContent = response.description;
        popupContainer.classList.remove('hidden');
      } catch (error) {
        console.error('Error retrieving description:', error);
      }
    }, 1000);
  });

  cell.addEventListener('mouseleave', function () {
    clearTimeout(timeoutId);
    popupContainer.classList.add('hidden');
  });
});

async function getDescriptionFromFlask(dllName) {
  try {
    const response = await fetch(`/get-description/${dllName}`);
    const data = await response.json();
    return data;
  } catch (error) {
    throw new Error('Failed to retrieve description');
  }
}

function printTableToPDF(tableClass) {
var now = new Date();
var currentTime = now.toLocaleString();
tableName = "DLL List"
//Retrieve table content
var table = document.querySelector(tableClass);
var rows = table.rows;

//Convert table rows to array of arrays
var dataRows = [];
for (var i = 0; i < rows.length; i++) {
  var rowData = [];
  for (var j = 0; j < rows[i].cells.length; j++) {
    rowData.push(rows[i].cells[j].textContent);
  }
  dataRows.push(rowData);
}

//Create document definition
var docDefinition = {
  pageSize: {
    width: 1000,
    height: 842
  },
  pageOrientation: "landscape",
  content: [
    { text:  currentTime + ' - ' + tableName, style: 'header' },
    {
      table: {
        headerRows: 1,
        widths: ['5%', '10%', '10%', '7%', '13%', '25%', '15%', '10%', '5%'],
        body: dataRows
        
      }
    }
  ],
  styles: {
    header: {
      fontSize: 18,
      bold: true,
      margin: [0, 0, 0, 10]
    }
  },
  defaultStyle: {
    font: 'Roboto'
  }
};

//Load Roboto font
var fonts = {
  Roboto: {
    normal: 'https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.66/fonts/Roboto/Roboto-Regular.ttf',
    bold: 'https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.66/fonts/Roboto/Roboto-Medium.ttf',
    italics: 'https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.66/fonts/Roboto/Roboto-Italic.ttf',
    bolditalics: 'https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.66/fonts/Roboto/Roboto-MediumItalic.ttf'
  }
};

//Create PDF document
var pdfDocGenerator = pdfMake.createPdf(docDefinition, null, fonts);

//Download PDF file
pdfDocGenerator.download(tableName + '.pdf');
}