// printing evaluation report
function printDiv() {
  var printContents = document.getElementById("print").innerHTML;
  var originalContents = document.body.innerHTML;

  document.body.innerHTML = printContents;

  window.print();

  document.body.innerHTML = originalContents;
}

document.getElementById("sidebarToggle").addEventListener("click", function () {
  var sidebar = document.getElementById("sidebar");
  var content = document.getElementById("content");
  var navbar = document.getElementById("navbar");

  sidebar.querySelectorAll(".collapse.show").forEach((collapseable) => {
    collapseable.classList.remove("show");
  });

  sidebar.classList.toggle("collapsed");
  content.classList.toggle("collapsed");
  navbar.classList.toggle("collapsed");
  document.body.classList.toggle("collapsed");
});

document.querySelectorAll(".sidebar .sidebar-item").forEach((item) => {
  item.addEventListener("click", () => {
    document.querySelectorAll(".sidebar .show").forEach((active_item) => {
      // active_item is the open section
      // the open section should contain the selected "item"
      if (
        !(
          active_item.classList.contains("section-lead") &&
          active_item.contains(item)
        )
      ) {
        // if selected item is in an open section e.g. Prospect in
        // loan processing, the loan processing section should not close
        active_item.classList.toggle("show");
      }
    });
    if (item.closest(".sidebar").classList.contains("collapsed")) {
      document.getElementById("sidebar").classList.toggle("collapsed");
      document.getElementById("content").classList.toggle("collapsed");
      document.getElementById("navbar").classList.toggle("collapsed");
    }
  });

  if (item.classList.contains("active")) {
    item.classList.add("collapsed");

    let collapseId = item.href.split("#").reverse()[0];
    try {
      let itemLinksArea = sidebar.querySelector(`#${collapseId}`);
      itemLinksArea.classList.add("show");
    } catch {}
  }
});

document.querySelectorAll(".form-part-minimizer").forEach((minimizer) => {
  minimizer.addEventListener("click", () => {
    let modalFormArea = minimizer.closest(".modal-form-area");
    modalFormArea.querySelector(".modal-form").classList.toggle("hide-fields");
    modalFormArea.classList.toggle("hide-fields");

    let showedIcon = minimizer.parentNode.querySelector("i.show");
    let hiddenIcon = minimizer.parentNode.querySelector("i.hidden");

    showedIcon.classList.toggle("show");
    showedIcon.classList.toggle("hidden");

    hiddenIcon.classList.toggle("show");
    hiddenIcon.classList.toggle("hidden");
  });
});

document.querySelectorAll(".card-body-minimizer").forEach((minimizer) => {
  minimizer.addEventListener("click", () => {
    let card = minimizer.closest(".card");
    card.querySelector(".card-body").classList.toggle("hide-fields");
    card.classList.toggle("hide-fields");

    let showedIcon = minimizer.parentNode.querySelector("i.show");
    let hiddenIcon = minimizer.parentNode.querySelector("i.hidden");

    showedIcon.classList.toggle("show");
    showedIcon.classList.toggle("hidden");

    hiddenIcon.classList.toggle("show");
    hiddenIcon.classList.toggle("hidden");
  });
});

// asset form selection
document
  .querySelectorAll(".asset-type-selector .selector")
  .forEach((selector) => {
    // get selected form area
    let targetformArea = document.querySelector(
      `#${selector.getAttribute("data-asset-select-form-id")}`,
    );

    selector.addEventListener("click", () => {
      document
        .querySelector(".asset-type-selector .selector.active")
        .classList.toggle("active");
      selector.classList.toggle("active");
      // hide existing form areas
      document
        .querySelectorAll(".asset-selection-forms > div.show")
        .forEach((formArea) => {
          formArea.classList.remove("show");
          formArea.classList.add("hidden");
        });

      targetformArea.classList.remove("hidden");
      targetformArea.classList.add("show");
    });
  });

document.querySelectorAll(".asset-selection-forms > div.hidden");

document
  .querySelectorAll("form .asset-selection-forms > div.hidden input")
  .forEach((elem) => {
    if (elem.required == true) {
      elem.required = false;
    }
  });

// Transaction ID valuation
function getCSRFToken() {
  let csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
  return csrfToken;
}

// function verifyPayment(prospectpk) {
//   // Show SweetAlert2 input form
//   Swal.fire({
//     title: "Enter Transaction ID",
//     input: "text",
//     inputLabel: "Please enter the Transaction ID (TID)",
//     inputPlaceholder: "Enter TID here",
//     showCancelButton: true,
//     confirmButtonText: "Submit",
//     preConfirm: (tid) => {
//       if (!tid) {
//         Swal.showValidationMessage("TID is required!");
//       }
//       // console.log(tid)
//       return tid;
//     },
//   }).then((result) => {
//     if (result.isConfirmed) {
//       const tid = result.value;
//       // console.log(tid)

//       // Make a POST request to store the TID and verify
//       fetch(`/prospect_valuation/valuation-details/${prospectpk}/`, {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//           "X-CSRFToken": getCSRFToken(),
//         },
//         body: JSON.stringify({ tid: tid }),
//       })
//         .then((response) => response.json())
//         .then((data) => {
//           if (data.saved) {
//             Swal.fire({
//               icon: "success",
//               title: "TID Saved Successfully",
//               text: "TID has been saved and will be compared with the extracted TID.",
//             });

//             setTimeout(() => window.location.reload(), 2000);
//           } else {
//             Swal.fire({
//               icon: "error",
//               title: "Error",
//               text: "TID supplied doesnot match. Please provide a Valid TID.",
//             });
//           }
//         })
//         .catch((error) => {
//           console.error("Error:", error);
//           Swal.fire({
//             icon: "error",
//             title: "Invalid Transaction ID",
//             text: "The TID supplied has already been used. Please provide a Valid Transaction ID.",
//           });
//         });
//     }
//   });
// }

function printSchedule() {
  var printContents = document.getElementById("printableArea").innerHTML;
  var originalContents = document.body.innerHTML;

  // Replace body content with the printable area
  document.body.innerHTML = printContents;

  // Trigger the print dialog
  window.print();

  // Restore original page content after printing
  document.body.innerHTML = originalContents;

  // Reload the original JavaScript behavior
  window.location.reload();
}

document.addEventListener("DOMContentLoaded", function () {
  var inputField = document.getElementById("id_v_market_value");
  var inputField2 = document.getElementById("id_v_forced_sale");

  // Ensure the element exists before adding the event listener
  if (inputField != null) {
    inputField.addEventListener("input", function (e) {
      // Remove commas and non-numeric characters
      let value = e.target.value.replace(/,/g, "").replace(/[^0-9]/g, "");

      // Format the number with commas for thousands
      e.target.value = new Intl.NumberFormat("en-US").format(value);
    });
  }
  if (inputField2 != null) {
    inputField2.addEventListener("input", function (e) {
      // Remove commas and non-numeric characters
      let value = e.target.value.replace(/,/g, "").replace(/[^0-9]/g, "");

      // Format the number with commas for thousands
      e.target.value = new Intl.NumberFormat("en-US").format(value);
    });
  }

  let payment_amount_paid = document.getElementById("payment_amount_paid");
  if (payment_amount_paid != null) {
    payment_amount_paid.addEventListener("input", function (e) {
      // Remove commas and non-numeric characters
      let value = e.target.value.replace(/,/g, "").replace(/[^0-9]/g, "");

      // Format the number with commas for thousands
      e.target.value = new Intl.NumberFormat("en-US").format(value);
    });
  }
});

if (document.getElementById("exceptional_amount") != undefined) {
  document
    .getElementById("exceptional_amount")
    .addEventListener("input", function (e) {
      let value = e.target.value.replace(/[^0-9]/g, ""); // Remove non-numeric characters
      let numericValue = parseFloat(value) / 100; // Convert to float and divide by 100

      // Format as currency for display
      e.target.value = new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "UGX",
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(numericValue);
    });
}

if (document.getElementById("id_ap_reviewer_recommended_amount") != undefined) {
  document
    .getElementById("id_ap_reviewer_recommended_amount")
    .addEventListener("input", function (e) {
      let value = e.target.value.replace(/[^0-9]/g, ""); // Remove non-numeric characters

      // Format the number with commas for thousands
      e.target.value = new Intl.NumberFormat("en-US", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(value);
    });
}

// for handling showing the Next button after disbursement and offer letter have been clicked
document.addEventListener("DOMContentLoaded", function () {
  // Initialize states from localStorage or set them to false initially
  let offerClicked = localStorage.getItem("offerClicked") === "true";
  let disbursementClicked =
    localStorage.getItem("disbursementClicked") === "true";

  const offerLetterBtn = document.getElementById("offer-letter-btn");
  const disbursementBtn = document.getElementById("disbursement-btn");
  const nextBtnContainer = document.getElementById("next-btn-container");
  const buttonContainer = document.getElementById("button-container");

  // If both buttons were clicked previously, show the 'Next' button
  checkBothClicked();

  // Add event listeners for button clicks
  if (offerLetterBtn != null) {
    offerLetterBtn.addEventListener("click", function () {
      localStorage.setItem("offerClicked", "true"); // Mark offer button as clicked
    });
  }

  if (disbursementBtn != null) {
    disbursementBtn.addEventListener("click", function () {
      localStorage.setItem("disbursementClicked", "true"); // Mark disbursement button as clicked
    });
  }

  // Function to check if both buttons were clicked and show the 'Next' button
  function checkBothClicked() {
    if (offerClicked && disbursementClicked && nextBtnContainer != null) {
      nextBtnContainer.style.display = "block"; // Show the 'Next' button
      buttonContainer.style.display = "none"; // Hide the buttons
    }
  }
});

document.addEventListener("DOMContentLoaded", function () {
  // Calculate the number of days from today to 30 days in the future
  var today = new Date();
  var futureDate = new Date(today);
  futureDate.setDate(today.getDate() + 30);
  var timeDiff = futureDate - today;
  var daysUntilFutureDate = Math.ceil(timeDiff / (1000 * 3600 * 24));

  // Display the counter in the paragraph tag
  if (document.getElementById("counter") != null) {
    document.getElementById("counter").innerText = daysUntilFutureDate;
  }
});

// handle product field change in order to fetch product details to display
document.addEventListener("DOMContentLoaded", function () {
  var inputField = document.getElementById("id_estimated_affordability");
  var inputField2 = document.getElementById("id_average_financials");
  const productField = document.getElementById("product");
  if (productField != null) {
    productField.addEventListener("change", function () {
      const selectedProductId = productField.value;

      if (selectedProductId) {
        // Make AJAX request to fetch product details
        const url = `${window.location.origin}/loan-applications/product-details-fetch/${selectedProductId}/`; // Use product ID

        fetch(url)
          .then((response) => response.json())
          .then((data) => {
            if (data.error) {
              console.error(data.error);
            } else {
              // Update the min and max amount spans
              document.getElementById("min_amount").textContent =
                data.min_principal_amount;
              document.getElementById("max_amount").textContent =
                data.max_principal_amount;
              document.getElementById("max_interest").textContent =
                data.max_interest_rate;
              document.getElementById("min_interest").textContent =
                data.min_interest_rate;
              document.getElementById("min_repayment_period").textContent =
                data.min_repayment_period;
              document.getElementById("max_repayment_period").textContent =
                data.max_repayment_period;
              // document.getElementById("product_interest_rate").value = data.interest_rate;
              document.getElementById("interest_method").value =
                data.interest_method;

              // set fees
              //
              fees_table = document.querySelector("#fees-container tbody");
              fees_table.innerHTML = "";

              for (const key in data.fees_data) {
                if (data.fees_data.hasOwnProperty(key)) {
                  const fees_table_row = document.createElement("tr");
                  fees_table_row.innerHTML = `
                    <td>
                        <p>${key}</p>
                    </td>
                    <td>
                        <input
                            type="number"
                            name="min ${key}"
                            id="{{loan_fee.name}}"
                            class="form-control"
                            value="${data.fees_data[key]["min"]}"
                        />
                    </td>
                    <td>
                        <input
                            type="number"
                            name="default ${key}"
                            id="{{loan_fee.name}}"
                            class="form-control"
                            value="${data.fees_data[key]["default"]}"
                        />
                    </td>
                    <td>
                        <input
                            type="number"
                            name="max ${key}"
                            id="{{loan_fee.name}}"
                            class="form-control"
                            value="${data.fees_data[key]["max"]}"
                        />
                    </td>
                  `;
                  fees_table.appendChild(fees_table_row);
                }
              }
            }
          })
          .catch((error) =>
            console.error("Error fetching product details:", error),
          );
      } else {
        // Reset the amounts if no product is selected
        document.getElementById("min_amount").textContent = "";
        document.getElementById("max_amount").textContent = "";
      }
    });
  }
  if (inputField != undefined) {
    inputField.addEventListener("input", function (e) {
      // Remove commas and non-numeric characters
      let value = e.target.value.replace(/,/g, "").replace(/[^0-9]/g, "");

      // Format the number with commas for thousands
      e.target.value = new Intl.NumberFormat("en-US").format(value);
    });
  }
  if (inputField2 != undefined) {
    inputField2.addEventListener("input", function (e) {
      // Remove commas and non-numeric characters
      let value = e.target.value.replace(/,/g, "").replace(/[^0-9]/g, "");

      // Format the number with commas for thousands
      e.target.value = new Intl.NumberFormat("en-US").format(value);
    });
  }
});
// Handle the form submission via AJAX
if (document.getElementById("submitLoanApplicationForm") != null) {
  document
    .getElementById("submitLoanApplicationForm")
    .addEventListener("click", function (event) {
      event.preventDefault(); // Prevent default form submission

      const form = document.getElementById("loanApplicationForm");
      const formData = new FormData(form);

      fetch(form.action, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            // If form submission is successful, close the modal and refresh the page
            const modal = bootstrap.Modal.getInstance(
              document.getElementById("loanApplicationModal"),
            );
            modal.hide();
            location.reload(); // Refresh to update the view with the new application status
          } else {
            // Display form errors
            document.getElementById("form-errors").style.display = "block";
            document.getElementById("form-errors").innerHTML =
              data.non_field_errors;

            // Clear old field errors
            document.querySelectorAll(".text-danger").forEach((errorDiv) => {
              errorDiv.innerHTML = "";
            });

            // Show field-specific errors
            for (const [field, errors] of Object.entries(data.errors)) {
              document.getElementById(`${field}-error`).innerHTML =
                errors.join("<br>");
            }
          }
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    });
}

document.addEventListener("DOMContentLoaded", function () {
  // const aveFinancialsInput = document.getElementById("id_average_financials");
  // const estimatedAffordabilityInput = document.getElementById(
  //   "id_estimated_affordability",
  // );
  const amountRequestedInput = document.getElementById("id_amount_requested");
  const teamleaderAmountInput = document.getElementById(
    "teamLeader_recommended_amount",
  );

  if (teamleaderAmountInput != null) {
    teamleaderAmountInput.addEventListener("input", function (e) {
      let rawValue = e.target.value.replace(/[^0-9]/g, ""); // Remove non-numeric characters
      e.target.value = formatNumber(rawValue); // Format as number with commas
    });
  }

  // Format the teamleader recommended amount with commas
  if (teamleaderAmountInput != null) {
    teamleaderAmountInput.addEventListener("input", function (e) {
      let rawValue = e.target.value.replace(/[^0-9]/g, ""); // Remove non-numeric characters
      e.target.value = formatNumber(rawValue); // Format as number with commas
    });
  }

  // Function to format numbers with commas (no decimal places)
  function formatNumber(value) {
    // Remove non-numeric characters
    value = value.replace(/[^0-9]/g, "");
    const number = parseFloat(value);
    if (!isNaN(number)) {
      return new Intl.NumberFormat("en-US").format(number); // Format with commas
    }
    return ""; // Return an empty string if the value is not a number
  }

  // Format the amount requested field with commas
  if (amountRequestedInput != null) {
    amountRequestedInput.addEventListener("input", function (e) {
      let rawValue = e.target.value.replace(/[^0-9]/g, ""); // Remove non-numeric characters
      e.target.value = formatNumber(rawValue); // Format as number with commas
    });
  }

  // AJAX form submission
  $(document).ready(function () {
    $("#loanApplicationForm").submit(function (event) {
      event.preventDefault(); // Prevent form from submitting the traditional way
      var formData = new FormData(this);

      $.ajax({
        type: "POST",
        url: $(this).attr("action"),
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
          // Handle success (e.g., close modal, refresh part of the page)
          $("#loanApplicationModal").modal("hide");
          // Optionally reload the page or update specific parts with new data
        },
        error: function (response) {
          // Handle errors
          console.log(response);
        },
      });
    });
  });
});

// if (document.getElementById("id_ap_reviewer_recommended_amount") != null) {
//   document
//     .getElementById("id_ap_reviewer_recommended_amount")
//     .addEventListener("input", function (e) {
//       let value = e.target.value.replace(/[^0-9]/g, ""); // Remove non-numeric characters
//       let numericValue = parseFloat(value) / 100; // Convert to float and divide by 100

//       // Format as currency for display
//       e.target.value = new Intl.NumberFormat("en-US", {
//         style: "currency",
//         currency: "UGX",
//         minimumFractionDigits: 0,
//         maximumFractionDigits: 0,
//       }).format(numericValue);
//     });
// }
document.addEventListener("DOMContentLoaded", function () {
  const opAmount = document.getElementById("id_ap_recommended_amount");
  if (opAmount != null) {
    opAmount.addEventListener("input", function (e) {
      // Remove commas and non-numeric characters
      let value = e.target.value.replace(/,/g, "").replace(/[^0-9]/g, "");

      // Format the number with commas for thousands
      e.target.value = new Intl.NumberFormat("en-US").format(value);
    });
  }
});

// if (document.getElementById("id_sales_manager_recommended_amount") != null) {
//   document
//     .getElementById("id_sales_manager_recommended_amount")
//     .addEventListener("input", function (e) {
//       let value = e.target.value.replace(/[^0-9]/g, ""); // Remove non-numeric characters
//       let numericValue = parseFloat(value); // Convert to float and divide by 100
//       // teamleaderAmountInput.addEventListener("input", function (e) {
//       //   let rawValue = e.target.value.replace(/[^0-9]/g, ""); // Remove non-numeric characters
//       //   e.target.value = formatNumber(rawValue); // Format as number with commas
//       // });
//       function formatNumber(value) {
//         // Remove non-numeric characters
//         value = value.replace(/[^0-9]/g, "");
//         const number = parseFloat(value);
//         if (!isNaN(number)) {
//           return new Intl.NumberFormat("en-US").format(number); // Format with commas
//         }
//         return ""; // Return an empty string if the value is not a number
//       }

//       // Format as currency for display
//       // e.target.value = new Intl.NumberFormat("en-US", {
//       //   // style: "currency",
//       //   style: "decimal",
//       //   // currency: "UGX",
//       //   minimumFractionDigits: 0,
//       //   maximumFractionDigits: 0,
//       // }).format(numericValue);
//     });
// }

document.addEventListener("DOMContentLoaded", function () {
  const opAmount = document.getElementById(
    "id_sales_manager_recommended_amount",
  );
  if (opAmount != null) {
    opAmount.addEventListener("input", function (e) {
      // Remove commas and non-numeric characters
      let value = e.target.value.replace(/,/g, "").replace(/[^0-9]/g, "");

      // Format the number with commas for thousands
      e.target.value = new Intl.NumberFormat("en-US").format(value);
    });
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const opAmount = document.getElementById("id_ops_recommended_amount");
  if (opAmount != null) {
    opAmount.addEventListener("input", function (e) {
      // Remove commas and non-numeric characters
      let value = e.target.value.replace(/,/g, "").replace(/[^0-9]/g, "");

      // Format the number with commas for thousands
      e.target.value = new Intl.NumberFormat("en-US").format(value);
    });
  }
});

document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("date") != null) {
    var today = new Date();
    var options = { year: "numeric", month: "long", day: "numeric" };
    var formattedDate = today.toLocaleDateString("en-US", options);
    document.getElementById("date").innerText = formattedDate;
  }

  document
    .querySelectorAll("#loan_fees_type input[type='radio']")
    .forEach((input) => {
      input.addEventListener("change", () => {
        const percentage_fields = document.querySelector("#percentage_fields");
        if (!input.id.toUpperCase().includes("PERCENTAGE")) {
          percentage_fields.classList.add("disabled-area");
          percentage_fields
            .querySelectorAll("input[type='radio']")
            .forEach((inner_input) => {
              inner_input.disabled = true;
            });
        } else {
          percentage_fields.classList.remove("disabled-area");
          percentage_fields
            .querySelectorAll("input[type='radio']")
            .forEach((inner_input) => {
              inner_input.disabled = false;
            });
        }
      });
    });
  document.querySelectorAll(".alert button").forEach((btn) => {
    btn.addEventListener("click", () => {
      btn.closest(".alert").classList.add("hidden");
    });
  });

  // auto select all permissions
  let select_all_permissions_cta = document.querySelector(
    "#select_all_permissions",
  );
  if (select_all_permissions_cta != null) {
    select_all_permissions_cta.addEventListener("change", () => {
      document
        .querySelectorAll(
          ".permission-select-area input[type='checkbox'].permission-option",
        )
        .forEach((elem) => {
          if (select_all_permissions_cta.checked == true) {
            elem.checked = true;
          } else {
            elem.checked = false;
          }
        });
    });
  }

  // loan product
  const approval_criteria_table = document.querySelector(
    ".approval-criteria-table",
  );

  const reassignRowIndexs = () => {
    if (
      document.querySelectorAll(".approval-criteria-table tbody tr").len <= 0
    ) {
      return;
    }
    document
      .querySelectorAll(".approval-criteria-table tbody tr")
      .forEach((row, i) => {
        row.setAttribute("data-row-index", i);
      });
  };

  if (approval_criteria_table != null) {
    const add_approval_criteria_cta = document.querySelector(
      "#add-approval-criteria-cta",
    );

    // already existing rows
    approval_criteria_table
      .querySelectorAll("tbody tr .row-delete-cta")
      .forEach((cta) =>
        cta.addEventListener("click", () => {
          cta.closest("tr").remove();
          reassignRowIndexs();
        }),
      );

    add_approval_criteria_cta.addEventListener("click", (e) => {
      e.preventDefault();

      const last_item = approval_criteria_table.querySelector(
        "tbody tr:last-of-type",
      );

      let last_row_index;
      if (last_item == null) {
        last_row_index = -1;
      } else {
        last_row_index = last_item.getAttribute("data-row-index");
      }
      let new_row_index = parseInt(last_row_index) + 1;

      // create new criteria
      const row_item = document.createElement("tr");
      row_item.setAttribute("data-row-index", new_row_index);
      row_item.innerHTML = `
          <td>
              <input class="form-control" type="text" list="car-makes" id="car-make" name="approval-criteria-car-make-${new_row_index}">
          </td>
          <td>
              <input class="form-control" type="text" name="approval-criteria-license-series-${new_row_index}">
          </td>
          <td>
              <input class="form-control" type="number" min="0" max="100" name="approval-criteria-percentage-${new_row_index}">
          </td>
          <td>
              <select id="car-select" name="approval-criteria-applicable-on-${new_row_index}" class="form-control" style="text-align:center">
                  <option value="">--Please choose an option--</option>
                  <option value="Market Value">Market Value</option>
                  <option value="Forced Value">Forced Value Value</option>
              </select>
          </td>
          <td>
              <span class="row-delete-cta">
                  <i class="fa fa-trash"></i>
              </span>
          </td>
        `;
      approval_criteria_table.querySelector("tbody").appendChild(row_item);

      row_item.querySelectorAll("tbody tr .row-delete-cta").forEach((cta) =>
        cta.addEventListener("click", () => {
          cta.closest("tr").remove();
          // reassign data-row-index for database loop to work
          reassignRowIndexs();
        }),
      );
    });
  }

  // enforcing approval criteria on approval form
  const approval_form__recommended_amount_ids = [
    "id_sales_manager_recommended_amount",
    "id_ops_recommended_amount",
    "id_ap_reviewer_recommended_amount",
  ];
  for (let i = 0; i < approval_form__recommended_amount_ids.length; i++) {
    const inputField = document.querySelector(
      `#${approval_form__recommended_amount_ids[i]}`,
    );
    if (inputField != null) {
      inputField.addEventListener("keyup", (e) => {
        // UGX 20,000,000.00
        let value = parseFloat(
          e.target.value.split("UGX").reverse()[0].trim().split(",").join(""),
        );

        if (!document.querySelector(".approval-criteria-warning")) {
          return;
        }
        let max_value = parseFloat(
          document
            .querySelector(".approval-criteria-warning")
            .getAttribute("data-max-amount")
            .split(",")
            .join(""),
        );

        if (value > max_value) {
          e.target.value = `UGX ${max_value.toLocaleString("en-US")}`;
          document
            .querySelectorAll(".approval-criteria-warning")
            .forEach((elem) => elem.classList.add("emphasize"));
        } else {
          document
            .querySelectorAll(".approval-criteria-warning")
            .forEach((elem) => elem.classList.remove("emphasize"));
        }
      });
    }
  }

  document
    .querySelectorAll(
      "table:not(.card-body table):not(.loan-schedule):not(form table):not(.recommendation-card table)",
    )
    .forEach((table) => {
      try {
        const dbtable = new DataTable(table, {
          order: [],
        });
      } catch (error) {}
    });

  document.querySelectorAll(".chart-card .btn-box-tool").forEach((btn) => {
    btn.addEventListener("click", () => {
      let data_widget = btn.getAttribute("data-widget");
      let icon = btn.querySelector("i");

      if (data_widget == "collapse") {
        btn.setAttribute("data-widget", "open");
        icon.classList.remove("fa-minus");
        icon.classList.add("fa-plus");
        btn.closest(".chart-card").classList.add("collapsed");
      } else if (data_widget == "remove") {
        btn.closest(".chart-card").remove();
      } else if (data_widget == "open") {
        icon.classList.remove("fa-plus");
        icon.classList.add("fa-minus");
        btn.closest(".chart-card").classList.remove("collapsed");
        btn.setAttribute("data-widget", "collapse");
      }
    });
  });

  const settings_search = document.querySelector("#settings-search");
  if (settings_search != null) {
    settings_search.addEventListener("keyup", (e) => {
      let search_value = e.target.value.trim();
      document.querySelectorAll(".setting-item").forEach((item) => {
        if (search_value.trim() == "") {
          item.style.display = "block";
          document
            .querySelectorAll(".setttings-group")
            .forEach((list) => (list.style.display = "block"));
          return;
        }
        if (
          !item.textContent
            .trim()
            .toLowerCase()
            .includes(search_value.toLowerCase())
        ) {
          item.style.display = "none";
        } else {
          item.style.display = "block";
        }

        document.querySelectorAll(".setttings-group").forEach((list) => {
          if (
            list.querySelectorAll('.setting-item:not([style*="display: none"]')
              .length < 1
          ) {
            list.style.display = "none";
          } else {
            list.style.display = "block";
          }
        });
      });
    });
  }

  let year_of_manufacture = document.querySelector("#id_year_of_manufacture");
  let date_of_registration = document.querySelector("#id_date_of_registration");
  let years_since_on_uganda_roads = document.querySelector(
    "#id_years_since_on_uganda_roads",
  );

  if (years_since_on_uganda_roads != null) {
    years_since_on_uganda_roads.readOnly = true;
  }

  if (
    year_of_manufacture != null &&
    date_of_registration != null &&
    years_since_on_uganda_roads != null
  ) {
    date_of_registration.addEventListener("change", () => {
      const date = new Date(date_of_registration.value);
      const year = date.getFullYear();

      const currentDate = new Date();
      const currentYear = currentDate.getFullYear();

      console.log(Number(year_of_manufacture.value), year);
      console.log(Number(year_of_manufacture.value) > year);
      if (year < Number(year_of_manufacture.value) || currentDate < date) {
        date_of_registration.style.border = "2px solid red";
        year_of_manufacture.style.border = "2px solid red";
        date_of_registration
          .closest("form")
          .querySelector("button").style.display = "none";
      } else {
        date_of_registration.style.border = "1px solid #ced4da";
        year_of_manufacture.style.border = "1px solid #ced4da";
        date_of_registration
          .closest("form")
          .querySelector("button").style.display = "block";
      }

      // set years on ugandan roads based on date_of_registration
      years_since_on_uganda_roads.value = currentYear - year;
    });
  }

  function numberToWords(num) {
    const ones = [
      "",
      "One",
      "Two",
      "Three",
      "Four",
      "Five",
      "Six",
      "Seven",
      "Eight",
      "Nine",
      "Ten",
      "Eleven",
      "Twelve",
      "Thirteen",
      "Fourteen",
      "Fifteen",
      "Sixteen",
      "Seventeen",
      "Eighteen",
      "Nineteen",
    ];
    const tens = [
      "",
      "",
      "Twenty",
      "Thirty",
      "Forty",
      "Fifty",
      "Sixty",
      "Seventy",
      "Eighty",
      "Ninety",
    ];
    const thousands = ["", "Thousand", "Million", "Billion"];

    if (num === 0) return "Zero";

    let words = "";
    let i = 0;

    // Split the number into chunks of three digits
    while (num > 0) {
      if (num % 1000 !== 0) {
        words = helper(num % 1000) + thousands[i] + " " + words;
      }
      num = Math.floor(num / 1000);
      i++;
    }

    return words.trim();

    // Helper function to convert numbers from 1 to 999
    function helper(n) {
      if (n === 0) return "";
      if (n < 20) return ones[n] + " ";
      if (n < 100) return tens[Math.floor(n / 10)] + " " + ones[n % 10] + " ";
      return ones[Math.floor(n / 100)] + " Hundred " + helper(n % 100);
    }
  }

  document.querySelectorAll(".make-words").forEach((elem) => {
    // remove currency if any
    let v = elem.textContent.trim().split(" ");

    // remove decimals
    v = v[v.length - 1].split(".")[0];
    // remove commas
    v = v.split(",").join("");
    if (isNaN(v)) {
      return;
    }
    let value = parseInt(v);

    let words = numberToWords(value);

    if (words) {
      if (elem.getAttribute("data-type") == "amount") {
        words = `${words} shillings`;
      } else if (elem.getAttribute("data-type") == "percentage") {
        words = `${words} percentage`;
      }
    }

    elem.innerHTML = `${value.toLocaleString("en-US")} - ${words}`;
  });

  const exceptional_approval = document.querySelector("#exceptional_approval");
  const other_reason = document.querySelector("#other_reason");
  if (exceptional_approval != null) {
    const expectional_request_basis = document.querySelector(
      "#expectional_request_basis",
    );
    if (expectional_request_basis != null) {
      exceptional_approval.addEventListener("change", (e) => {
        if (e.target.checked == true) {
          expectional_request_basis.style.display = "grid";
        }
      });

      other_reason.addEventListener("change", (e) => {
        if (e.target.checked == true) {
          console.log(expectional_request_basis);
          expectional_request_basis.style.display = "none";
        }
      });
    }
  }

  // uploaded content preview

  document
    .querySelectorAll("input[type='file'], input[type='image']")
    .forEach((elem) =>
      elem.addEventListener("change", (e) => {
        const fileInput = e.target;

        // create preview area
        e.target.parentNode.style.display = "grid";
        e.target.parentNode.style.gap = "1rem";

        const previewContainer = document.createElement("div");
        previewContainer.className = "previewContainer";
        previewContainer.style.display = "grid";
        previewContainer.style.gap = "1rem";
        e.target.parentNode.appendChild(previewContainer);

        // Clear previous preview
        previewContainer.innerHTML = "";

        // Check if a file was selected
        if (fileInput.files && fileInput.files[0]) {
          const file = fileInput.files[0];
          const fileName = file.name;
          const fileType = file.type;

          if (fileType.startsWith("image/")) {
            // If the file is an image, preview it
            const reader = new FileReader();
            reader.onload = function (e) {
              const img = document.createElement("img");
              img.src = e.target.result;
              img.style.maxWidth = "100%";
              img.style.height = "250px";
              previewContainer.appendChild(img);
            };
            reader.readAsDataURL(file);
          } else if (fileType === "application/pdf") {
            // If the file is a PDF, provide a link to view it
            const pdfLink = document.createElement("a");
            pdfLink.href = URL.createObjectURL(file);
            pdfLink.target = "_blank";
            pdfLink.innerHTML = `<p style="font-size: 12px; display: grid;grid-auto-flow: column; gap: .25rem;justify-content:flex-start;"><span style="color: blue;">View PDF:</span> <span> ${fileName}</span></p>`;
            previewContainer.appendChild(pdfLink);
          } else if (
            fileType === "application/msword" ||
            fileType ===
              "application/vnd.openxmlformats-officedocument.wordprocessingml.document" ||
            fileType === "text/plain"
          ) {
            // If the file is a Word document or text file, show its name
            const docLink = document.createElement("a");
            docLink.href = URL.createObjectURL(file);
            docLink.target = "_blank";
            docLink.innerHTML = `<p style="font-size: 12px; display: grid;grid-auto-flow: column; gap: .25rem;justify-content:flex-start;"><span style="color: blue;">View Document:</span> <span> ${fileName}</span></p>`;
            previewContainer.appendChild(docLink);
          } else {
            // For unsupported file types, show a message
            previewContainer.textContent = `File type not supported for preview: ${fileName}`;
          }
        } else {
          // If no file was selected
          previewContainer.textContent = "No file selected.";
        }
      }),
    );
});

// customizations for mobile view
document.addEventListener("DOMContentLoaded", () => {
  const mb_menu_cta = document.querySelector("#mb-menu-cta");
  if (mb_menu_cta != null) {
    mb_menu_cta.addEventListener("click", () => {
      const icon = mb_menu_cta.querySelector("i");
      const navbar = mb_menu_cta.closest(".navbar");
      if (navbar.classList.contains("open-menu")) {
        icon.classList.replace("fa-close", "fa-bars");
        navbar.classList.remove("open-menu");
      } else {
        icon.classList.replace("fa-bars", "fa-close");
        navbar.classList.add("open-menu");
      }
    });
  }

  document.querySelectorAll("img").forEach((img) => {
    img.addEventListener("click", () => {
      let zoomer = document.querySelector(".img-zoomer");
      zoomer.querySelector("img").src = img.src;
      zoomer.classList.add("show");
      zoomer.querySelector(".close-cta").addEventListener("click", () => {
        zoomer.classList.remove("show");
      });
    });
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const makeField = document.getElementById("id_make");
  const customMakeWrapper = document.getElementById("customMakeWrapper");
  const customMakeField = document.getElementById("id_custom_make");

  if (makeField != null) {
    makeField.addEventListener("change", function () {
      if (makeField.value.toLowerCase() === "other") {
        customMakeWrapper.style.display = "block";
      } else {
        customMakeWrapper.style.display = "none";
      }
      // Show custom make input if "OTHER" is selected
    });
  }

  if (customMakeField != null) {
    customMakeField.addEventListener("keyup", () => {
      makeField.value = customMakeField.value;
    });
  }

  // On form submission, if "OTHER" is selected, set makeField value to customMakeField value
  // what for are we adding the event listener to?
  // lets be specific
  if (document.querySelector("form")) {
    document.querySelector("form").addEventListener("submit", function (event) {
      if (
        makeField != null &&
        customMakeField != null &&
        makeField.value === "OTHER" &&
        customMakeField.value.trim() !== ""
      ) {
        makeField.value = customMakeField.value; // Replace make value with custom input
      }
    });
  }
});
