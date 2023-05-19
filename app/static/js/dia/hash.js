function printTableToPDF(tableClass) {
    var now = new Date();
    var currentTime = now.toLocaleString();
    if (tableClass == ".current-hash-table") {
      tableName = "Current Hashes";
    }
    else if (tableClass == ".original-hash-table") {
      tableName = "Original Hashes";
    }
    else if (tableClass == ".changed-hash-table") {
      tableName = "Changed Hashes";
    }
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
            widths: ['50%', '25%', '25%'],
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
    pdfDocGenerator.download(tableClass + '.pdf');
  }

  const popupContainer = document.querySelector("#popup-container");

  function showPopupIfNecessary() {
    const changedHashTable = document.querySelector(".changed-hash-table");
    const hasChangedHashes = changedHashTable && changedHashTable.querySelector("tr.hash-changed");
    
    if (hasChangedHashes) {
      popupContainer.classList.add("visible");
    } else {
      popupContainer.classList.remove("visible");
    }
  }

  window.addEventListener("load", showPopupIfNecessary);
  window.addEventListener("hashes-changed", showPopupIfNecessary);
  
  popupContainer.addEventListener("click", function() {
    //Hide the popup container by adding the "hidden" class
    popupContainer.classList.add("hidden");
    const changedHashTable = document.querySelector(".changed-hash-table");
    changedHashTable.scrollIntoView({ behavior: "smooth" });
  });
  
  popupContainer.addEventListener("click", function() {
    popupContainer.classList.remove("visible");
  });
  