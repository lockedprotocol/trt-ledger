// Generated from data.json by checker/check_prices.py — edit data.json, not this file.
window.TRT_DATA = {
  "buttondownUsername": "trtledger",
  "updated": "2026-11-03",
  "clinics": [
    {
      "id": "henry-meds",
      "name": "Henry Meds",
      "url": "https://henrymeds.com",
      "sourceUrl": "https://henrymeds.com/terms-of-service/programs",
      "checked": "2026-11-03",
      "verified": true,
      "model": "Flat monthly",
      "monthly": 129,
      "intakeFee": 0,
      "labsIncluded": true,
      "labFee": 0,
      "medsIncluded": true,
      "clinicYear1Estimate": null,
      "forms": [
        "injection",
        "cream",
        "oral",
        "enclomiphene"
      ],
      "aiIncluded": true,
      "hcg": "Not listed",
      "commitment": "No commitment listed",
      "states": "Not listed on pricing page",
      "highlights": [
        "Up to 1,000 mg test cypionate per 28 days + injection kit",
        "Anastrozole (AI) included",
        "Oral Kyzatrex option at $179/mo (not in CA)",
        "Compounded pharmacy fulfillment"
      ],
      "watchOuts": [
        "States served not on pricing page"
      ],
      "watch": [
        {
          "field": "monthly",
          "pattern": "Testosterone Replacement Therapy.{0,400}?\\$(\\d+(?:\\.\\d\\d)?) per month"
        }
      ],
      "priceByForm": {
        "oral": 179
      }
    },
    {
      "id": "trt-nation",
      "name": "TRT Nation",
      "url": "https://trtnation.com",
      "sourceUrl": "https://trtnation.com",
      "checked": "2026-11-03",
      "verified": true,
      "model": "Flat monthly",
      "monthly": 99,
      "intakeFee": 0,
      "labsIncluded": false,
      "labFee": null,
      "medsIncluded": true,
      "clinicYear1Estimate": null,
      "forms": [
        "injection"
      ],
      "aiIncluded": null,
      "hcg": "Not listed",
      "commitment": "Cancellation policy linked, terms not shown",
      "states": "All except AL, AK, AR, MO, ND, HI",
      "highlights": [
        "Meds, supplies and FedEx shipping included",
        "Bring your own labs (up to 6 months old)",
        "10% off first treatment"
      ],
      "watchOuts": [
        "Labs extra or bring your own; lab price not published",
        "Must be 24+",
        "Some testimonials on the site look unreliable"
      ],
      "watch": [
        {
          "field": "monthly",
          "pattern": "Testosterone Replacement Therapy \\$(\\d+)/mo"
        }
      ]
    },
    {
      "id": "defy-medical",
      "name": "Defy Medical",
      "url": "https://www.defymedical.com",
      "sourceUrl": "https://www.defymedical.com/faq/how-much-does-trt-cost-with-defy-medical/",
      "checked": "2026-11-03",
      "verified": true,
      "model": "Pay per service",
      "monthly": null,
      "monthlyLabel": "~$175 avg",
      "intakeFee": null,
      "labsIncluded": true,
      "labFee": null,
      "medsIncluded": true,
      "clinicYear1Estimate": 2100,
      "forms": [],
      "aiIncluded": true,
      "hcg": "Not listed",
      "commitment": "No subscription or contract",
      "states": "Not listed on pricing page",
      "highlights": [
        "No monthly membership fee",
        "Clinic's own average: under $175/mo year 1, ~$125/mo after",
        "Average includes testosterone, weekly AI, labs and consults"
      ],
      "watchOuts": [
        "Averages are illustrative; your cost depends on protocol"
      ],
      "watch": [
        {
          "field": "clinicYear1Estimate",
          "pattern": "under \\$(\\d+) per month for the first year",
          "multiply": 12
        },
        {
          "field": "ongoingMonthly",
          "pattern": "around \\$(\\d+) per month"
        }
      ],
      "ongoingMonthly": 125
    },
    {
      "id": "fountain-trt",
      "name": "Fountain TRT",
      "url": "https://www.fountaintrt.com",
      "sourceUrl": "https://www.fountaintrt.com",
      "checked": "2026-11-03",
      "verified": true,
      "model": "Flat monthly",
      "monthly": 199,
      "intakeFee": 0,
      "labsIncluded": null,
      "labFee": null,
      "medsIncluded": true,
      "clinicYear1Estimate": null,
      "forms": [
        "injection"
      ],
      "aiIncluded": null,
      "hcg": "Not listed",
      "commitment": "Cancel anytime",
      "states": "AL, AZ, CA, CO, CT, FL, GA, IL, IN, MI, NJ, NY, NC, OH, PA, TN, TX, VA, WA, WI",
      "highlights": [
        "\"As low as $199/mo, all inclusive\"",
        "Medication, video visits, ongoing support",
        "Follow-ups every 3–6 months"
      ],
      "watchOuts": [
        "Unclear whether partner-lab fees are covered",
        "Only 20 states"
      ],
      "watch": [
        {
          "field": "monthly",
          "pattern": "as low as \\$(\\d+) per month"
        }
      ]
    },
    {
      "id": "hone-health",
      "name": "Hone Health",
      "url": "https://honehealth.com",
      "sourceUrl": "https://honehealth.com",
      "checked": "2026-11-03",
      "verified": true,
      "model": "Membership + meds",
      "monthly": 155,
      "intakeFee": 65,
      "labsIncluded": true,
      "labFee": 0,
      "medsIncluded": false,
      "clinicYear1Estimate": null,
      "forms": [],
      "aiIncluded": null,
      "hcg": "Not listed",
      "commitment": "No commitment, cancel anytime",
      "states": "Not listed",
      "highlights": [
        "$65 start: 50+ biomarker labs + physician consult",
        "Premium $155/mo: retests and follow-ups every 90 days",
        "Basic $25/mo tier (labs every 6 months, no protocol)"
      ],
      "watchOuts": [
        "Medication billed on top of membership; price not published"
      ],
      "watch": [
        {
          "field": "monthly",
          "pattern": "\\$(\\d+) ?/month plus cost of medication",
          "pick": "max"
        },
        {
          "field": "intakeFee",
          "pattern": "For just \\$(\\d+), you"
        }
      ]
    },
    {
      "id": "marek-health",
      "name": "Marek Health",
      "url": "https://marekhealth.com",
      "sourceUrl": "https://marekhealth.com",
      "checked": "2026-11-03",
      "verified": true,
      "model": "Pay as you go",
      "monthly": null,
      "monthlyLabel": "$80–200 treatment",
      "intakeFee": 299,
      "labsIncluded": false,
      "labFee": 450,
      "medsIncluded": false,
      "clinicYear1Estimate": 1599,
      "forms": [],
      "aiIncluded": null,
      "hcg": "Not listed",
      "commitment": "No subscription",
      "states": "Not listed",
      "highlights": [
        "45-min health coach session + provider exam in intake",
        "Deep lab panels (from $450)",
        "HSA/FSA commonly used"
      ],
      "watchOuts": [
        "Highest upfront cost ($299 + $450 labs)",
        "Doesn't bill insurance"
      ],
      "watch": [
        {
          "field": "intakeFee",
          "pattern": "\\$(\\d+) to get started"
        },
        {
          "field": "clinicYear1Estimate",
          "pattern": "Year 1 avg\\. spend\\*? ~\\$\\d+ ?/mo ~\\$([\\d,]+) annual"
        },
        {
          "field": "ongoingMonthly",
          "pattern": "Year 2\\+ avg\\. spend\\*? ~\\$(\\d+) ?/mo"
        }
      ],
      "ongoingMonthly": 70
    },
    {
      "id": "hims",
      "name": "Hims",
      "url": "https://www.hims.com",
      "sourceUrl": "https://www.hims.com/blog/how-much-does-testosterone-cost",
      "checked": "2026-11-02",
      "verified": true,
      "model": "Prepaid plan",
      "monthly": 99,
      "intakeFee": 0,
      "labsIncluded": null,
      "labFee": null,
      "medsIncluded": true,
      "clinicYear1Estimate": null,
      "forms": [
        "enclomiphene"
      ],
      "aiIncluded": false,
      "hcg": "No",
      "commitment": "$99/mo requires 10-month plan",
      "states": "Not listed",
      "highlights": [
        "Enclomiphene (boosts your own T) — not testosterone"
      ],
      "watchOuts": [
        "Not TRT",
        "Headline price needs a 10-month commitment"
      ]
    },
    {
      "id": "peter-md",
      "name": "PeterMD",
      "url": "https://www.getpetermd.com",
      "sourceUrl": "https://www.getpetermd.com/mens-trt/",
      "checked": "2026-11-03",
      "verified": true,
      "model": "Prepaid plan",
      "monthly": 79,
      "prepaid": 948,
      "intakeFee": 0,
      "labsIncluded": null,
      "labFee": null,
      "medsIncluded": true,
      "clinicYear1Estimate": null,
      "forms": [
        "injection",
        "enclomiphene"
      ],
      "aiIncluded": null,
      "hcg": "Add-on, $301 per 10,000 IU vial",
      "commitment": "$79/mo needs 12-month prepay ($948); $109/mo on 6 months; $139/mo month-to-month",
      "states": "All except AL, ID",
      "highlights": [
        "Medications and free shipping included",
        "Unlimited provider access, 90-day check-in",
        "Labs at Quest, or use recent bloodwork",
        "HSA/FSA eligible; 20% price-match offer"
      ],
      "watchOuts": [
        "Cheapest price is paid upfront for 12 months",
        "Prepaid plans roll into monthly billing — read the auto-bill policy",
        "Unclear whether lab fees are included"
      ],
      "watch": [
        {
          "field": "monthly",
          "pattern": "\\$(\\d+)/ ?Month 12-Month Plan"
        },
        {
          "field": "prepaid",
          "pattern": "12-Month Plan[^$]{0,40}\\$\\d+ Yearly Savings \\$([\\d,]+) total"
        }
      ]
    },
    {
      "id": "fridays",
      "name": "Fridays",
      "url": "https://www.joinfridays.com",
      "sourceUrl": "https://www.joinfridays.com/testosterone",
      "checked": "2026-11-03",
      "verified": true,
      "model": "Flat monthly",
      "monthly": 129,
      "intakeFee": 0,
      "labsIncluded": null,
      "labFee": null,
      "medsIncluded": null,
      "clinicYear1Estimate": null,
      "forms": [
        "injection",
        "oral",
        "enclomiphene"
      ],
      "aiIncluded": true,
      "hcg": "Not listed",
      "commitment": "No commitments, cancel anytime",
      "states": "Not listed",
      "highlights": [
        "Injectable or oral testosterone from $129/mo",
        "Free baseline labs at Quest or Labcorp",
        "Anastrozole included when clinically appropriate",
        "Free shipping"
      ],
      "watchOuts": [
        "Follow-up labs at 1 and 3 months, then quarterly — cost not stated",
        "Outside lab results not accepted",
        "\"From\" price; unclear if meds are included"
      ],
      "watch": [
        {
          "field": "monthly",
          "pattern": "From \\$(\\d+) ?/mo",
          "pick": "min"
        }
      ]
    },
    {
      "id": "joi-blokes",
      "name": "Joi + Blokes",
      "url": "https://joiandblokes.com",
      "sourceUrl": "https://joiandblokes.com",
      "checked": "2026-11-03",
      "verified": true,
      "model": "Flat monthly",
      "monthly": 99,
      "intakeFee": 0,
      "labsIncluded": false,
      "labFee": null,
      "medsIncluded": true,
      "clinicYear1Estimate": null,
      "forms": [],
      "aiIncluded": null,
      "hcg": "Not listed",
      "commitment": "No term stated",
      "states": "Not listed",
      "highlights": [
        "$0 membership, $0 consults",
        "TRT or enclomiphene, both $99/mo",
        "Hormone panel $149 (56 biomarkers), advanced $399",
        "At-home blood draws where available; health coach"
      ],
      "watchOuts": [
        "Labs paid separately",
        "At-home blood draw fee not shown until checkout"
      ],
      "watch": [
        {
          "field": "monthly",
          "pattern": "Prescription-based testosterone therapy\\. \\$(\\d+)/mo"
        }
      ]
    },
    {
      "id": "maximus",
      "name": "Maximus",
      "url": "https://www.maximustribe.com",
      "sourceUrl": "https://www.telehealthally.com/reviews/maximus-trt-review",
      "checked": "2026-11-02",
      "verified": false,
      "model": "Tiered by plan length",
      "monthly": 199.99,
      "intakeFee": 0,
      "labsIncluded": null,
      "labFee": null,
      "medsIncluded": true,
      "clinicYear1Estimate": null,
      "forms": [
        "cream",
        "oral",
        "enclomiphene"
      ],
      "aiIncluded": null,
      "hcg": "Not listed",
      "commitment": "Month-to-month price shown; cheaper on 3–12 month plans",
      "states": "Not listed",
      "highlights": [
        "Cream as low as $99.99/mo on 12-month plan (third-party report)",
        "Enclomiphene-first, fertility-friendly approach",
        "Coaching included (third-party report)"
      ],
      "watchOuts": [
        "Prices from review sites; official pricing page didn't load"
      ]
    },
    {
      "id": "nuform-health",
      "name": "Nuform Health",
      "url": "https://nuformhealth.com",
      "sourceUrl": "https://www.nuformhealth.com/trt",
      "checked": "2026-11-03",
      "verified": true,
      "model": "Prepaid kits",
      "monthly": 50,
      "intakeFee": 0,
      "labsIncluded": false,
      "labFee": null,
      "medsIncluded": true,
      "clinicYear1Estimate": null,
      "forms": [
        "injection",
        "enclomiphene"
      ],
      "aiIncluded": null,
      "hcg": "Offered as a 1-month injectable kit, testosterone plus hCG/gonadorelin, for $120/month (dosed at 200mg weekly, includes supplies).",
      "commitment": "Prepaid 4-month ($200) or 5-month ($295) kits; no monthly subscriptions",
      "states": "Not listed",
      "highlights": [
        "4-month injectable kit $200 ($50/month), includes medication and supplies",
        "5-month kit $295 ($59/mo)",
        "SubQ or IM, and micro-dosing, at the same price",
        "Testosterone + hCG/gonadorelin kit $120/month",
        "Lab panels sold on their own diagnostic-labs page: Male Essential $95, Comprehensive $195 (Quest draw plus analysis fee)"
      ],
      "watchOuts": [
        "The low per-month price requires prepaying 4 to 5 months",
        "Kits have a fixed dose of 200mg weekly",
        "Labs are priced separately ($95 or $195 on the /diagnostic-labs page); the TRT page does not say labs are included",
        "No anastrozole, intake fee or states listed",
        "Enclomiphene is offered on a separate plan page; its price was not checked"
      ],
      "prepaid": 200,
      "watch": [
        {
          "field": "monthly",
          "pattern": "4 Month Injectable Kit[^$]{0,80}\\$ ?\\d+ \\(\\$(\\d+)/ ?month\\)"
        },
        {
          "field": "prepaid",
          "pattern": "4 Month Injectable Kit[^$]{0,80}\\$ ?(\\d+) \\(\\$\\d+/ ?month\\)"
        }
      ]
    },
    {
      "id": "feel30",
      "name": "Feel30",
      "url": "https://feel30.com",
      "sourceUrl": "https://feel30.com/product/injectable-testosterone-cypionate",
      "checked": "2026-11-03",
      "verified": true,
      "model": "Prepaid plan",
      "monthly": 149,
      "intakeFee": 0,
      "labsIncluded": true,
      "labFee": null,
      "medsIncluded": true,
      "clinicYear1Estimate": null,
      "forms": [
        "injection",
        "enclomiphene"
      ],
      "aiIncluded": null,
      "hcg": "Not mentioned on the TRT product page",
      "commitment": "$149/mo needs 12-month prepay ($1,788); $189/mo on 6 months; $229/mo month-to-month",
      "states": "Not listed",
      "highlights": [
        "Testosterone cypionate injections: $149/mo (12-mo prepaid), $189/mo (6-mo prepaid), $229/mo month-to-month",
        "Page says bloodwork, medication, doctor consults and shipping are included ('All-Inclusive Price No upsells. No hidden fees')",
        "At-home nurse visit or in-clinic lab option; vitamin D biomarker included",
        "Free 24-48hr shipping; 100% refundable if not eligible",
        "Guarantee of 10% total-testosterone increase for first-time patients or medication is free"
      ],
      "watchOuts": [
        "Headline $149/mo requires paying $1,788 upfront for 12 months; monthly-billed price is $229",
        "Strikethrough 'Starting at $399.99' reference price is a marketing anchor",
        "No anastrozole/AI or hCG mentioned",
        "States served not listed",
        "Page copy has inconsistencies (mentions Sermorelin and 'Oral TRT' on the injectable page; says 'no labs or appointments needed' while also advertising included lab work)"
      ],
      "prepaid": 1788,
      "watch": [
        {
          "field": "monthly",
          "pattern": "\\$(\\d+)/month Total \\$1,7"
        }
      ]
    },
    {
      "id": "rex-md",
      "name": "Rex MD",
      "url": "https://www.rexmd.com",
      "sourceUrl": "https://rexmd.com/our-medications/testosterone-program/",
      "checked": "2026-11-03",
      "verified": true,
      "model": "Flat monthly",
      "monthly": 250,
      "intakeFee": 99,
      "labsIncluded": true,
      "labFee": null,
      "medsIncluded": true,
      "clinicYear1Estimate": null,
      "forms": [
        "injection",
        "cream",
        "oral"
      ],
      "aiIncluded": null,
      "hcg": "Not mentioned",
      "commitment": "Monthly subscription with quarterly shipments; minimum term and cancellation terms not stated",
      "states": "Not listed",
      "highlights": [
        "$99 one-time initial fee includes a lab panel and a video consultation",
        "$250 to $299/month includes medication, ongoing lab tests and at least one video consult per year",
        "Options include testosterone cypionate injection, testosterone gel, Clomid tablets and sermorelin"
      ],
      "watchOuts": [
        "$250 is the floor; some medications cost up to $299/month",
        "Shipments are quarterly",
        "Labs required 90 days after start, then every six months",
        "No anastrozole, hCG or states listed"
      ],
      "watch": [
        {
          "field": "monthly",
          "pattern": "as low as \\$(\\d+) per month"
        }
      ]
    },
    {
      "id": "male-excel",
      "name": "Male Excel",
      "url": "https://maleexcel.com",
      "sourceUrl": "https://maleexcel.com/treatments/hrt-costs/",
      "checked": "2026-11-03",
      "verified": true,
      "model": "Membership + meds",
      "monthly": 219,
      "intakeFee": 99,
      "labsIncluded": null,
      "labFee": null,
      "medsIncluded": true,
      "clinicYear1Estimate": null,
      "forms": [
        "injection",
        "cream",
        "oral"
      ],
      "aiIncluded": null,
      "hcg": "Not mentioned",
      "commitment": "No Contract, Cancel Anytime; billed every other month",
      "states": "Not listed",
      "highlights": [
        "Injectable testosterone from $120/mo plus required $99/mo medical membership (= $219/mo)",
        "Topical Lipoderm cream with thyroid: starting at $132/month",
        "Oral Triclozene (clomiphene with thyroid): $95 to $120/month",
        "FSA/HSA eligible"
      ],
      "watchOuts": [
        "The required Medical Membership adds $99/month, so injectable TRT is about $219/month or more",
        "Shipping and handling is extra",
        "The headline 'as low as $95 a month' is for oral clomiphene (Triclozene), not testosterone",
        "Price varies with dose",
        "Lab costs are not shown on the pricing page"
      ],
      "watch": [
        {
          "field": "medPrice",
          "pattern": "\\$(\\d+)/month\\*"
        }
      ],
      "medPrice": 120
    },
    {
      "id": "viking-alternative-medicine",
      "name": "Viking Alternative Medicine",
      "url": "https://vikingalternative.com",
      "sourceUrl": "https://vikingalternative.com/pricing/",
      "checked": "2026-11-03",
      "verified": true,
      "model": "Flat monthly",
      "monthly": 100,
      "intakeFee": 0,
      "labsIncluded": null,
      "labFee": null,
      "medsIncluded": null,
      "clinicYear1Estimate": null,
      "forms": [
        "injection",
        "enclomiphene"
      ],
      "aiIncluded": null,
      "hcg": "Offered: 'Testosterone with or without HCG' packages (pricing not itemized)",
      "commitment": "Not stated; $25.00 charge for missed appointments without prior cancellation",
      "states": "All except AL, HI, MS (47 states via telemed)",
      "highlights": [
        "Pricing page gives a range: most patients pay $100-$150 a month (men and women)",
        "Exact cost depends on labs, protocol and treatment plan",
        "States 'No hidden fees, no insurance games'",
        "Telemed in 47 states; labs drawn at a local lab, meds shipped",
        "HRT packages with or without HCG; enclomiphene page also on site"
      ],
      "watchOuts": [
        "Price is a range: most patients pay $100–150/month depending on labs and protocol",
        "Only a range ($100-$150/mo) is published, not a fixed plan price; $100 used as the low end",
        "Pricing page does not say what is included (labs, meds, consults, AI) or list lab/intake fees",
        "$25 missed-appointment fee"
      ],
      "monthlyLabel": "$100–150/mo",
      "watch": [
        {
          "field": "monthly",
          "pattern": "Most Viking patients pay \\$(\\d+)"
        }
      ]
    },
    {
      "id": "bodylogicmd",
      "name": "BodyLogicMD",
      "url": "https://www.bodylogicmd.com",
      "sourceUrl": "https://www.bodylogicmd.com/pricing",
      "checked": "2026-11-03",
      "verified": true,
      "model": "Membership + meds",
      "monthly": 79,
      "intakeFee": 0,
      "labsIncluded": false,
      "labFee": null,
      "medsIncluded": false,
      "clinicYear1Estimate": null,
      "forms": [],
      "aiIncluded": null,
      "hcg": "Not mentioned",
      "commitment": "Month-to-month membership, cancel anytime, no long-term contracts",
      "states": "Not listed (network of ~60 clinic locations plus telehealth)",
      "highlights": [
        "BodyLogicMD Advantage membership $79/month",
        "Membership gives member pricing on hormone panels and treatments (BHRT)",
        "In-person or telehealth consults",
        "Cancel anytime, no insurance required"
      ],
      "watchOuts": [
        "$79/month is a membership fee only: hormone panels and treatments are billed separately at undisclosed 'member pricing'",
        "Pricing page is marketed to women (perimenopause/menopause BHRT); no men's TRT-specific price shown",
        "Consult, lab and medication costs not published",
        "Testosterone delivery forms not specified on the pricing page"
      ],
      "watch": [
        {
          "field": "monthly",
          "pattern": "For \\$(\\d+)/month, BodyLogicMD"
        }
      ]
    },
    {
      "id": "gameday-telehealth",
      "name": "Gameday Men's Health (telehealth)",
      "url": "https://gamedaymenshealth.com",
      "sourceUrl": "https://gamedaymenshealth.com/service/testosterone-replacement-therapy",
      "checked": "2026-11-03",
      "verified": true,
      "model": "Flat monthly",
      "monthly": 199,
      "intakeFee": 0,
      "labsIncluded": null,
      "labFee": null,
      "medsIncluded": null,
      "clinicYear1Estimate": null,
      "forms": [
        "injection",
        "enclomiphene",
        "oral"
      ],
      "aiIncluded": null,
      "hcg": "Not priced; HCG mentioned only as a blog topic",
      "commitment": "Not stated (telehealth page says 'Terms and restrictions may apply')",
      "states": "FL",
      "highlights": [
        "Testosterone Cypionate Injections, Testosterone Pellets and Clomid / Enclomiphene each listed at $199/mo on the TRT service page",
        "Oral TRT (Kyzatrex) offered, with no price shown",
        "Telehealth FAQ: 'Telemedicine services are currently only available in Florida.'"
      ],
      "watchOuts": [
        "The $199/mo prices are on the general TRT service page, and each card says 'Offered at select clinics'. The telehealth landing page (ldr.gamedaymenshealth.com/telehealth-lp) shows no prices.",
        "Telehealth page disclaimer: 'Prices and services may vary per location and are subject to change without warning.'",
        "The site says medical services are provided by independently owned and operated clinics (a franchise model).",
        "No intake, lab, or what's-included details are published.",
        "join.gamedaymenshealth.com/start-trt-treatment returned 404."
      ],
      "watch": [
        {
          "field": "monthly",
          "pattern": "Testosterone Cypionate Injections \\$(\\d+)/mo"
        }
      ]
    }
  ],
  "inPerson": [
    {
      "id": "ageless",
      "name": "Ageless Men's Health",
      "url": "https://www.agelessmenshealth.com",
      "locatorUrl": "https://www.agelessmenshealth.com/locations/",
      "checked": "2026-11-02",
      "pricing": "Not published",
      "locations": {
        "AZ": 9,
        "CA": 10,
        "CO": 3,
        "FL": 3,
        "GA": 3,
        "ID": 2,
        "IL": 5,
        "IN": 3,
        "IA": 1,
        "MS": 4,
        "NE": 2,
        "NV": 4,
        "NJ": 2,
        "NY": 4,
        "OH": 2,
        "PA": 4,
        "TN": 6,
        "TX": 8,
        "UT": 6,
        "VA": 2,
        "WA": 2
      },
      "statesReported": [],
      "everywhere": false,
      "notes": "85 clinics in 21 states (counted by hand; their site blocks automated checks)"
    },
    {
      "id": "low-t-center",
      "name": "Low T Center",
      "url": "https://lowtcenter.com",
      "locatorUrl": "https://lowtcenter.com/locations/",
      "checked": "2026-11-02",
      "pricing": "$25 first test · $135 confirmation + first shot · ~$105.50/mo injections · $135 follow-ups",
      "pricingSource": "https://lowtcenter.com/cost-of-treatment/",
      "locations": {
        "AR": 2,
        "CO": 3,
        "IL": 3,
        "IN": 2,
        "MO": 1,
        "NC": 1,
        "OH": 3,
        "OK": 2,
        "TN": 6,
        "TX": 36
      },
      "statesReported": [],
      "everywhere": false,
      "notes": "59 U.S. clinics in 10 states"
    },
    {
      "id": "gameday",
      "name": "Gameday Men's Health",
      "url": "https://gamedaymenshealth.com",
      "locatorUrl": "https://gamedaymenshealth.com/location-finder",
      "checked": "2026-11-02",
      "pricing": "Not published · free consult and free T test",
      "locations": {
        "AK": 1,
        "AL": 9,
        "AR": 2,
        "AZ": 16,
        "CA": 70,
        "CO": 11,
        "CT": 9,
        "DE": 1,
        "FL": 30,
        "GA": 16,
        "HI": 1,
        "IA": 3,
        "ID": 5,
        "IL": 11,
        "IN": 8,
        "KS": 4,
        "KY": 5,
        "LA": 4,
        "MA": 12,
        "MD": 6,
        "ME": 1,
        "MI": 10,
        "MN": 4,
        "MO": 6,
        "MT": 4,
        "NC": 14,
        "NE": 1,
        "NH": 3,
        "NJ": 13,
        "NM": 3,
        "NV": 3,
        "NY": 7,
        "OH": 12,
        "OK": 3,
        "OR": 3,
        "PA": 14,
        "RI": 2,
        "SC": 9,
        "SD": 3,
        "TN": 6,
        "TX": 43,
        "UT": 8,
        "VA": 14,
        "WA": 1,
        "WI": 8,
        "WV": 1
      },
      "statesReported": [],
      "everywhere": false,
      "notes": "420 U.S. clinics in 46 states"
    },
    {
      "id": "numale",
      "name": "VidaVital Medical (formerly NuMale)",
      "url": "https://www.vidavitalmedical.com",
      "locatorUrl": "https://www.vidavitalmedical.com/locations/",
      "checked": "2026-11-02",
      "pricing": "Not published",
      "locations": {
        "FL": 1,
        "NE": 1,
        "NM": 1,
        "NV": 1,
        "WI": 1
      },
      "statesReported": [],
      "everywhere": false,
      "notes": "5 U.S. clinics in 5 states"
    },
    {
      "id": "mantality",
      "name": "Mantality Health",
      "url": "https://mantalityhealth.com",
      "locatorUrl": "https://mantalityhealth.com/locations/",
      "checked": "2026-11-02",
      "pricing": "Not published",
      "locations": {
        "IA": 1,
        "MI": 1,
        "MO": 2,
        "NE": 1,
        "OH": 1,
        "WI": 2
      },
      "statesReported": [],
      "everywhere": false,
      "notes": "8 U.S. clinics in 6 states"
    }
  ],
  "noPricing": [
    {
      "name": "Evolve Telemed",
      "url": "https://evolvetelemed.com",
      "note": "Free consult; pricing only after you talk to an intake coordinator",
      "checked": "2026-11-02"
    },
    {
      "name": "Ways2Well",
      "url": "https://ways2well.com",
      "note": "Care-plan tiers include labs; no prices on site. Not in MO, NJ, NY, RI",
      "checked": "2026-11-02"
    },
    {
      "name": "Keeps TRT (formerly Titan)",
      "url": "https://jointitan.com",
      "note": "$49 to start (labs + consult); monthly price only shown inside its sign-up quiz",
      "checked": "2026-11-03"
    },
    {
      "name": "Ehormones MD",
      "url": "https://ehormones.com",
      "note": "Prices not published on its site",
      "checked": "2026-11-03"
    },
    {
      "name": "Huddle Men's Health",
      "url": "https://huddlemenshealth.com",
      "note": "Prices not published; telehealth in CA and WA",
      "checked": "2026-11-03"
    }
  ],
  "labs": [
    {
      "test": "Total testosterone",
      "vendor": "Ulta Lab Tests",
      "lab": "Quest",
      "price": 29.95,
      "fees": 12.95,
      "sourceUrl": "https://www.findlabtest.com/lab-test/hormone-testing/testosterone-total-males-adult-ia-quest-result-code-55036300",
      "checked": "2026-11-03",
      "verified": false,
      "watch": [
        {
          "field": "total",
          "pattern": "\\$([\\d.]+) Order Ulta Lab Tests"
        }
      ]
    },
    {
      "test": "Total testosterone",
      "vendor": "Walk-In Lab",
      "lab": "Quest",
      "price": 59.0,
      "fees": 0,
      "sourceUrl": "https://www.findlabtest.com/lab-test/hormone-testing/testosterone-blood-test-quest-873",
      "checked": "2026-11-02",
      "verified": false
    },
    {
      "test": "Bioavailable + total testosterone",
      "vendor": "Walk-In Lab",
      "lab": "Quest",
      "price": 139.0,
      "fees": 0,
      "sourceUrl": "https://www.findlabtest.com/lab-test/hormone-testing/testosterone-free-bioavailable-and-total-ms-quest-14966",
      "checked": "2026-11-02",
      "verified": false
    },
    {
      "test": "Free & weakly bound testosterone",
      "vendor": "Walk-In Lab",
      "lab": "LabCorp",
      "price": 139.0,
      "fees": 0,
      "sourceUrl": "https://www.findlabtest.com/lab-test/general-wellness/testosterone-free-and-weakly-bound-labcorp-143255",
      "checked": "2026-11-02",
      "verified": false
    },
    {
      "test": "Male hormone panel",
      "vendor": "Ulta Lab Tests",
      "lab": "Quest",
      "price": 299.95,
      "fees": 12.95,
      "sourceUrl": "https://www.findlabtest.com/lab-test/hormone-testing/testosterone-blood-test-quest-873",
      "checked": "2026-11-02",
      "verified": false
    }
  ],
  "recentChanges": []
};
