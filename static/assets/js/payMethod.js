// Get Stripe publishable key
fetch("/config")
    .then((result) => { return result.json(); })
    .then((data) => {

        var stripe = Stripe(data.publicKey);

        document.querySelector("button").disabled = true;


        fetch("/create-setup-intent", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                }
            })
            .then(function(result) {
                return result.json();
            })
            .then(function(data) {
                var elements = stripe.elements({ clientSecret: data.clientSecret });

                // Create and mount the Payment Element
                var paymentElement = elements.create("payment");
                paymentElement.mount('#payment-element');

                paymentElement.on("change", function(event) {
                    // Disable the Pay button if there are no card details in the Element
                    document.querySelector("button").disabled = event.empty;
                    document.querySelector("#card-error").textContent = event.error ? event.error.message : "";
                });

                var form = document.getElementById("payment-form");

                form.addEventListener('submit', async(event) => {
                    event.preventDefault();

                    const { error } = await stripe.confirmSetup({
                        //`Elements` instance that was used to create the Payment Element
                        elements,
                        confirmParams: {
                            return_url: 'http://' + document.domain + ':' + location.port + '/home',
                        }
                    });

                    if (error) {
                        // This point will only be reached if there is an immediate error when
                        // confirming the payment. Show error to your customer (for example, payment
                        // details incomplete)
                        const messageContainer = document.querySelector('#error-message');
                        messageContainer.textContent = error.message;
                    } else {
                        // Your customer will be redirected to your `return_url`. For some payment
                        // methods like iDEAL, your customer will be redirected to an intermediate
                        // site first to authorize the payment, then redirected to the `return_url`.
                    }
                });
            });


        /* ------- UI helpers ------- */


        // Show a spinner on payment submission
        var loading = function(isLoading) {
            if (isLoading) {
                // Disable the button and show a spinner
                document.querySelector("button").disabled = true;
                document.querySelector("#spinner").classList.remove("hidden");
                document.querySelector("#button-text").classList.add("hidden");
            } else {
                document.querySelector("button").disabled = false;
                document.querySelector("#spinner").classList.add("hidden");
                document.querySelector("#button-text").classList.remove("hidden");
            }
        };

    });