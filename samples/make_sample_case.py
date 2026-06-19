from fpdf import FPDF

TEXT = """IN THE HIGH COURT OF JUDICATURE AT DELHI

CIVIL APPEAL NO. 4521 OF 2021

Ramesh Kumar Agarwal ... Appellant
versus
Sunrise Textiles Pvt. Ltd. ... Respondent

JUDGMENT

1. This appeal arises out of a judgment and decree dated 14 March 2020 passed by the
learned District Judge, South Delhi, in Civil Suit No. 112 of 2018, whereby the suit filed
by the appellant for recovery of Rs. 18,50,000 along with interest was dismissed.

2. The appellant, a supplier of raw cotton, entered into a written agreement dated
2 January 2017 with the respondent, a textile manufacturing company, for the supply of
500 quintals of raw cotton at a price of Rs. 6,200 per quintal, to be delivered in four
equal instalments over six months. The agreement contained a clause requiring payment
within 30 days of each delivery.

3. The appellant's case is that three instalments were duly delivered and accepted by
the respondent, but payment for the second and third instalments, amounting to
Rs. 18,50,000, was never made despite repeated reminders and a legal notice dated
9 August 2017.

4. The respondent's defence was that the cotton delivered in the second and third
instalments did not conform to the quality specifications agreed between the parties,
namely a minimum staple length and moisture content threshold specified in Schedule A
to the agreement, and that the respondent was therefore entitled to withhold payment
under Clause 9 of the agreement, which permits the buyer to reject non-conforming goods.

5. The trial court accepted the respondent's defence, relying primarily on an inspection
report prepared by the respondent's own quality control department, and held that the
appellant had failed to prove conformity with the agreed specifications. The suit was
accordingly dismissed with costs.

6. Before this Court, the appellant contends that the trial court erred in relying solely
on an inspection report prepared unilaterally by the respondent, without any independent
or joint inspection as contemplated under Clause 11 of the agreement, which required
both parties to be present at the time of quality testing. The appellant further submits
that the respondent's conduct in accepting and using the cotton in its manufacturing
process for several months after delivery, without raising any contemporaneous objection,
amounts to a waiver of any right to reject the goods on grounds of quality.

7. We find merit in the appellant's submission. Clause 11 of the agreement is unambiguous
in requiring a joint inspection. The respondent's unilateral inspection report, prepared
without notice to or participation by the appellant, cannot by itself discharge the
respondent's burden of proving non-conformity, particularly where the respondent has
gone on to use the goods in its production process. Acceptance and use of goods for an
extended period, without timely objection, is ordinarily inconsistent with a subsequent
claim of non-conformity.

8. For these reasons, we are of the view that the trial court's finding cannot be
sustained. The judgment and decree dated 14 March 2020 are set aside. The respondent is
directed to pay the appellant a sum of Rs. 18,50,000 together with interest at 9% per
annum from the date of the legal notice, namely 9 August 2017, until realisation.

9. The appeal is allowed. The respondent shall also bear the appellant's costs of these
proceedings, quantified at Rs. 75,000.

Ordered accordingly.
"""


def main():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 6, TEXT)
    pdf.output("samples/sample_civil_appeal.pdf")
    print("Wrote samples/sample_civil_appeal.pdf")


if __name__ == "__main__":
    main()
