package req_extract;

import java.awt.geom.Rectangle2D;
import java.io.File;
import java.io.PrintWriter;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.text.PDFTextStripperByArea;

public class PDFParser {

	private String[] abbreviations = new String[] { "Sec.", "Sect.", "i.e.", "e.g.", "I.e.", "E.g.", "Etc.", "etc.", "Techn.", "Ch.", "ch.", "Pt."};

	public String pdfPath;
	public File pdfFile;
	public String xmlPath;
	public PDDocument pdfDocument;



	public PDFParser(String PDFPath, String xmlPath) throws Exception {
		this.pdfPath = PDFPath;
		this.pdfFile = new File(PDFPath);
		this.pdfDocument = PDDocument.load(pdfFile);
		this.xmlPath = xmlPath;
	}

	public void writeXML(String s) {
		try (PrintWriter fileWriter = new PrintWriter(xmlPath)) {
			fileWriter.write(s);
		} catch (Exception e) {
			System.out.println("Cannot write to /home/ole/Documents/req.xml");
			System.exit(-1);
		}
		System.out.println("Successfully printed xml to " + xmlPath);
	}


	/**
	 * Reading only the inner part of the document excluding header and footer
	 *
	 */
	public String readTextByArea(PDDocument doc, int startPage, int endPage) throws Exception {

		// Equinor has top text 0-70
		// content in 70-450
//		int headerHeight = 70;
//		int pageHeight = 450;

		// DNVGL-ST-F101 has top text 0-50
		// content from 50-700
		int headerHeight = 50;
		int pageHeight= 650;
		int headerStart = 0;
		int width = 550;
		//int height = 50;


		int footerStart = headerHeight + pageHeight;

		Rectangle2D headerRegion = new Rectangle2D.Double(0, headerStart, width, headerHeight);
		Rectangle2D footerRegion = new Rectangle2D.Double(0, footerStart, width, headerHeight);
		Rectangle2D contentRegion = new Rectangle2D.Double(0, headerStart + headerHeight, width, pageHeight);

		String headerRegionName = "header";
		String footerRegionName = "footer";
		String contentRegionName = "content";

		PDFTextStripperByArea stripper = new PDFTextStripperByArea();
		stripper.setParagraphStart("\t");
		stripper.setSortByPosition(true);
		stripper.addRegion(headerRegionName, headerRegion);
		stripper.addRegion(footerRegionName, footerRegion);
		stripper.addRegion(contentRegionName, contentRegion);

		String content = "";
		for (int pageNumber = startPage; pageNumber < endPage; pageNumber++) {
			PDPage page = doc.getPage(pageNumber + 1);
			stripper.extractRegions(page);
			content += stripper.getTextForRegion(contentRegionName);
		}
		return content;
	}

	/**
	 * This removes . from common abbreviations
	 *
	 * @param s
	 * @return
	 */
	public String abbreviationFilter(String s) {
		// fix to not split sentences on abbreviations
		for (String abbrev : abbreviations) {
			String source = abbrev;
			String target = source.replace(".", " ");
			s = s.replace(source, target);
		}
		return s;
	}


	public String parseRequirement(String s, String theme, String title, String edition) {

		boolean usePart = false;
		boolean useChapter = false;
		boolean useSection = true;
		boolean useSub = true;
		boolean useSub2 = true;
		boolean useSub3 = true; /* hard to combined with use3levelreq*/
		boolean use_3_level_req = true;

		String partHeader = "^.?(\\d\\d?)\\s+([A-Z].*[^.])$";

//		String chapterHeader = "CHAPTER\\s(\\d\\d?)\\s(.*)";
//		String chapterHeader = "^.?Chapter\\s+(\\d\\d?)\\s+(.*)";
		String chapterHeader = "^.?Chapter\\s+(\\d\\d?)\\s+(.*)";
//		String chapterHeader = "^.?CHAPTER\\s+(\\d\\d?)\\s+(.*)";

		String sectionHeader = "SECTION\\s(\\d\\d?)\\s(.*)";
		String appendixSectionHeader = "APPENDIX\\s(\\w)\\s(.*)";

		String sub1_regex = "\\t(\\d\\d?)\\s+([A-Z][a-z].*)"; /* 1 Introduction */
		String sub2_regex = "^\\t?(\\d\\d?\\.\\d\\d?)\\s+([A-Z/].*)"; /* 1.1 General */
//		String sub2_regex_without_title = "^.?(\\d\\d?\\.\\d\\d?)\\s?(?=\\n[A-Za-z][A-Za-z\\-\\.]{30})"; /* 11.1\nThis is a section */
		String sub2_regex_without_title = "^.?([1-9]\\d?\\.[1-9]\\d?).?$"; /* 11.1\nThis is a section */

		//String sub3_regex = "^\\t?(\\d\\d?\\.\\d\\d?\\.\\d\\d?)\\s+([A-Z/].*)"; /* 1.1.1 Scope */
		String sub3_regex = "(^\\t\\d\\d?\\.\\d\\d?\\.\\d\\d?)\\s+([A-Z][A-Za-z\\s\\-]{3,60}(?=\\n))"; /* try to limit the length to distinguish from level3_req */


		//String req_num3 = "(^\\t\\d\\d?\\.\\d\\d?\\.\\d\\d?)\\s+([A-Z\\n].*)"; /* 1.1.1 Some requirement text possibly spanning several lines */
		String req_num3 = "(^\\t\\d\\d?\\.\\d\\d?\\.\\d\\d?)\\s+([A-Z0-9\\n].{20}.*)"; /* not allowing req with less than 20 characters */
		//String req_num4 = "(^\\t\\d\\d?\\.\\d\\d?\\.\\d\\d?\\.\\d\\d?)\\s+([A-Z/\n].*)"; /* 1.1.1.1 Some requirement text spanning several lines */
		String req_num4 = "(^\\t\\d\\d?\\.\\d\\d?\\.\\d\\d?\\.\\d\\d?)\\s+([A-Z\\n].{20}.*)"; /* 1.1.1.1 min 20 characters */





		s = s.replaceAll("\u00A0", " "); // Remove no-break space characters
		s = abbreviationFilter(s);
		System.out.println("Replacing non-xml characters");
		// Remove <, > and & symbols (to parse xml)
		s = s.replace(">", "&gt;");
		s = s.replace("<", "&lt;");
		s = s.replace("&", "and");

		/* CHAPTER 1 CLASSIFICATION */
		if (useChapter) {
			//System.out.println(s);
			System.out.println("Identifying Chapters");
			Matcher chapterHeaderMatcher = Pattern.compile(chapterHeader, Pattern.MULTILINE).matcher(s);
			s = chapterHeaderMatcher.replaceAll("<chapter num=\"$1\" title=\"$2\">");
		}

		if (useSection) {
			System.out.println("Identifying sections");
			/* SECTION 4 DESIGN - LOADS */
			/* identify section headers */
			s = s.replaceAll(sectionHeader, "<section num=\"$1\" title=\"$2\">");

			System.out.println("Identifying appendix sections");
			/* APPENDIX A TYPES AND MINIMUM DIMENSIONS */
			s = s.replaceAll(appendixSectionHeader, "<section num=\"$1\" title=\"$2\">");
		}




		/* 1 Material requirements */
		/* identify part haders: This is a level below section but before subsections.
		 * To avoid enumerate environment we have to check it doesn't end with a DOT */
		if (usePart) {
			System.out.println("Identifying parts");
			Matcher partHeaderMatcher = Pattern.compile(partHeader, Pattern.MULTILINE).matcher(s);
			s = partHeaderMatcher.replaceAll("\n<part num=\"$1\" title=\"$2\">");
		}

		if (useSub) {
			System.out.println("Identifying sub1");
			/* sub1: 4 1 General */
			//String subsec1Header = "\\t(\\d\\d?\\.\\d\\d?)\\s+([A-Z].*)"; /*note: added + */

			/* If sub1 has just one number */
			s = s.replaceAll(sub1_regex, "<sub1 num=\"$1\" title=\"$2\">");

			/* sub1: A 1 General */
			//String appendix1Header = "\\t(\\w\\.\\d\\d?)\\s+([A-Z].*)";
			//s = s.replaceAll(appendix1Header, "<sub1 num=\"$1\" title=\"$2\">");
		}



		/* We should identify these first */
		System.out.println("Identifying req (with 4 digits)");
		/* 4 1 1 1 Requirement */
		s = s.replaceAll(req_num4, "<req num=\"$1\">$2");

		if (useSub2) {
			System.out.println("Identifying sub2");
			/* sub2: 4 1 1 Objective */
			//String subsec2Header = "\\t(\\d\\d?\\.\\d\\d?\\.\\d\\d?)\\s+([A-Z].*)";
			//s = s.replaceAll(subsec2Header, "<sub2 num=\"$1\" title=\"$2\">");

			Pattern sub2_without_title_pattern = Pattern.compile(sub2_regex_without_title, Pattern.MULTILINE);
			Matcher sub2_without_title_matcher = sub2_without_title_pattern.matcher(s);
			s = sub2_without_title_matcher.replaceAll("<sub2 num=\"$1\">");

			//String req_num = "^\\t?(\\d\\d?\\.\\d\\d?\\.\\d\\d?)\\s+([A-Z/].*)"; /* note: added start of line anchor */
			Pattern sub2_pattern = Pattern.compile(sub2_regex, Pattern.MULTILINE);
			Matcher sub2_matcher = sub2_pattern.matcher(s);
			//s = req_num_matcher.replaceAll("<sub2 num=\"$1\" title=\"$2\">$2");
			s = sub2_matcher.replaceAll("<sub2 num=\"$1\" title=\"$2\">");


			/* sub2: A 1 1 Objective */
			//String appendix2Header= "\\t(\\w\\.\\d\\d?\\.\\d\\d?)\\s+([A-Z].*)";
			//s = s.replaceAll(appendix2Header, "<sub2 num=\"$1\" title=\"$2\">");
		}

		if (useSub3) {
			System.out.println("Identifying sub3");
			/* sub3: 4 1 1 Objective */
			//String subsec2Header = "\\t(\\d\\d?\\.\\d\\d?\\.\\d\\d?)\\s+([A-Z].*)";
			//s = s.replaceAll(subsec2Header, "<sub2 num=\"$1\" title=\"$2\">");

			//String req_num = "^\\t?(\\d\\d?\\.\\d\\d?\\.\\d\\d?)\\s+([A-Z/].*)"; /* note: added start of line anchor */
			Pattern sub3_pattern = Pattern.compile(sub3_regex, Pattern.MULTILINE);
			Matcher sub3_matcher = sub3_pattern.matcher(s);
			//s = req_num_matcher.replaceAll("<sub2 num=\"$1\" title=\"$2\">$2");
			s = sub3_matcher.replaceAll("<sub3 num=\"$1\" title=\"$2\">");



			/* sub3: A 1 1 Objective */
			String appendix2Header= "\\t(\\w\\.\\d\\d?\\.\\d\\d?).s+([A-Z].*)";
			s = s.replaceAll(appendix2Header, "<sub3 num=\"$1\" title=\"$2\">");
		}

		if (use_3_level_req) {
			System.out.println("Identifying req");
			/* 4 1 1 Requirement */
//			String req_num = "(\\d\\d?\\.\\d\\d?\\.\\d\\d?)\\s+([A-Z/].*)"; /* note: added + for RU-ship */
//			s = s.replaceAll(req_num, "<req num=\"$1\">$2");

			//String req_num = "^(\\d\\d?\\.\\d\\d?\\.\\d\\d?)\\s+([A-Z/].*)"; /* RU-shipCh4Pt8, pattern need start of line anchor */
			Pattern req_3_level_num_pattern= Pattern.compile(req_num3, Pattern.MULTILINE);
			Matcher req_num_matcher = req_3_level_num_pattern.matcher(s);
			s = req_num_matcher.replaceAll("<req num=\"$1\">$2");
		}





		/* A 1 1 1 Requirement */
		String appendix_req_num = "(\\w\\.\\d\\d?\\.\\d\\d?\\.\\d\\d?)\\s([A-Z].*)";
		s = s.replaceAll(appendix_req_num, "<req num=\"$1\">$2");

		System.out.println("Removing tab characters");
		/* remove all tab characters */
		s = s.replaceAll("\t", "");

		System.out.println("Identifying tables");
		/* Table 1-1 */
		String tab_num_double = "\\nTable\\s(\\d\\d?-\\d\\d?)(.*)";
		s = s.replaceAll(tab_num_double, "\n<table num=\"$1\">$2");

		/* Table A-1 */
		String appendix_tab_num_double = "^Table\\s(\\w-\\d\\d?)\\s([A-Z].*)";
		Pattern appendix_tab_pat = Pattern.compile(appendix_tab_num_double, Pattern.MULTILINE);
		Matcher appendix_tab_matcher = appendix_tab_pat.matcher(s);
		s = appendix_tab_matcher.replaceAll("\n<table num=\"$1\">$2");

		/* Table 1 */
		//String tab_num_single = "\\nTable\\s(\\d\\d?)(.*)";
		String tab_num_single = "Table.(\\d\\d?).([A-Z].*)";
		s = s.replaceAll(tab_num_single, "\n<table num=\"$1\" title=\"$2\">");

		System.out.println("Identifying figures");
		/* Figure 1-1 */
		String fig_num_double = "\\nFigure (\\d-\\d)\\s([A-Z].*)";
		s = s.replaceAll(fig_num_double, "\n<figure num=\"$1\">$2</figure>");

		/* Figure 1 */
		//String fig_num_single = "\\nFigure (\\d\\d?)\\s([A-Z].*)";
		String fig_num_single = "Figure.(\\d\\d?).([A-Z].*)";
		s = s.replaceAll(fig_num_single, "\n<figure num=\"$1\">$2</figure>");


		System.out.println("Identifying guidance notes");
		/* Guidance notes */
		s = s.replaceAll("Guidance note:", "<guidancenote>");
		s = s.replaceAll("Guidance note\\s(\\d)", "<guidancenote>");
//		s = s.replaceAll("Note:", "<note>");
		s = s.replaceAll("Guidance note:", "<guidancenote>");

		String guidanceNoteEnd = "---e-n-d---o-f---g-u-i-d-a-n-c-e---n-o-t-e---";
		String guidanceNoteEnd2 = "---e-n-d---of---g-u-i-d-a-n-c-e---n-o-t-e---";
		String guidanceNoteEnd3 = "---e-n-d---o-f---g-u-i-d-a-n-c-e---n-o-t-e--";
		String guidanceNoteEnd4 = "---e-n-d---o-f---g-u-i-d-a-n-c-e---n-o-t-e-";
		String guidanceNoteEnd5 = "---e-n-d---o-f---g-u-i-d-a-n-c-e---n-o-t-e";
		String guidanceNoteEnd6 = "---e-n-d---o-f---g-u-i-d-a-n-c-e---n-o-t-";
		String noteEnd = "---e-n-d---o-f---n-o-t-e---";
		s = s.replaceAll(guidanceNoteEnd, "</guidancenote>");
		s = s.replaceAll(guidanceNoteEnd2, "</guidancenote>"); // note: added for RU-ship pt2ch3
		s = s.replaceAll(guidanceNoteEnd3, "</guidancenote>");
		s = s.replaceAll(guidanceNoteEnd4, "</guidancenote>");
		s = s.replaceAll(guidanceNoteEnd5, "</guidancenote>");
		s = s.replaceAll(guidanceNoteEnd6, "</guidancenote>");
//		s = s.replaceAll(noteEnd, "</note>");
		s = s.replaceAll("<guidancenote>\\n", "<guidancenote>");
		s = s.replaceAll("\\n\\s</guidancenote>", "</guidancenote>");

		s = s.replaceAll("Interpretation:", "<interpretation>");
		String interpretationEnd = "---e-n-d---o-f---i-n-t-e-r-p-r-e-t-a-t-i-o-n---";
		s = s.replaceAll(interpretationEnd, "</interpretation>");



		if (!true) { // should be !useChapter but it doesn't work as supposed.
//			System.out.println(s);
			System.out.println("Removing everything before chapter 1");
			String sec1 = ".*?(<chapter num=\"1\".*)";
			Pattern sec1_pat = Pattern.compile(sec1, Pattern.MULTILINE | Pattern.DOTALL);
			Matcher sec1_matcher = sec1_pat.matcher(s);
			s = sec1_matcher.replaceFirst("$1"); // This does not work with Equinor-documents
		} else {
//			System.out.println(s);
			System.out.println("Remvoing everything before section 1");
			/* remove everything before section 1 */
			String sec1 = ".*?(<section num=\"1\".*)";
			Pattern sec1_pat = Pattern.compile(sec1, Pattern.MULTILINE | Pattern.DOTALL);
			Matcher sec1_matcher = sec1_pat.matcher(s);
			s = sec1_matcher.replaceFirst("$1"); // This does not work with Equinor-documents
		}

		System.out.println("Adding mandatory xml-elements");
		/* adding xml elements */
		s = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\" ?>\n<document theme=\"" + theme + "\" title=\"" + title + "\" edition=\"" + edition + "\">\n" + s;
		s = s + "</document>";


		System.out.println("Identifying end of table");
		/* END of table */
		String table_end = "(<table.*?>.*?)(?=(<document|<chapter|<part|<section|<sub|<req|<figure|<table|<guidancenote|</guidancenote))";
		Pattern table_end_pat = Pattern.compile(table_end, Pattern.DOTALL);
		Matcher table_end_matcher = table_end_pat.matcher(s);
		s = table_end_matcher.replaceAll("$1</table>\n");
		s = s.replaceAll("\\n</table>", "</table>");

		System.out.println("Identifying end of req");
		/* END OF req*/
		String req_end = "(<req.*?>.*?)(?=(<chapter|<section|<part|<sub|<req|</document))";
		Pattern req_end_pat = Pattern.compile(req_end, Pattern.DOTALL);
		Matcher req_end_matcher = req_end_pat.matcher(s);
		s = req_end_matcher.replaceAll("$1</req>\n");

		System.out.println("Remove newline before </req>");
		/* remove <newline> before </req> */
		s = s.replaceAll("\\n</req>", "</req>");


		System.out.println("Identifying end of table if it is within a requirement"); /* note: added this for RU-ship, doesn't always work*/
		/* END of table */
		String req_table_end = "(<req.*?>.*<table.*?>.*?)(?=</req)";
		Pattern req_table_end_pat = Pattern.compile(req_table_end, Pattern.DOTALL);
		Matcher req_table_end_matcher = req_table_end_pat.matcher(s);
		//s = req_table_end_matcher.replaceAll("$1</table>\n");
		//s = s.replaceAll("\\n</table>", "</table>");

		if (useSub3) {
			System.out.println("Identifying end of sub3");
			/* END OF sub2 */
			String sub3End = "(<sub3.*?>)(.*?)(?=(<sub1|<part|<sub2|<sub3|<section|<chapter|</document))"; // end with any of [sub1, sub2, sub3, section]
			Matcher sub3_end_matcher = Pattern.compile(sub3End, Pattern.DOTALL).matcher(s);
			s = sub3_end_matcher.replaceAll("$1$2</sub3>\n");
		}


		if (useSub2) {
			System.out.println("Identifying end of sub2");
			/* END OF sub2 */
			String sub2End = "(<sub2.*?>)(.*?)(?=(<sub1|<part|<sub2|<section|<chapter|</document))"; // end with any of [sub1, sub2, section]
			Matcher sub2_end_matcher = Pattern.compile(sub2End, Pattern.DOTALL).matcher(s);
			s = sub2_end_matcher.replaceAll("$1$2</sub2>\n");
		}

		System.out.println("Identifying end of sub1");
		/* END OF sub1 */
		String sub1End = "(<sub1.*?>)(.*?)(?=(<sub1|<part|<section|<chapter|</document))"; // end with [sub1 or section]
		Matcher sub1_end_matcher = Pattern.compile(sub1End, Pattern.DOTALL).matcher(s);
		s = sub1_end_matcher.replaceAll("$1$2</sub1>\n");

		System.out.println("Identifying end of part");
		/* END OF part */
		String partEnd = "(<part.*?>)(.*?)(?=(<part|<section|<chapter|</document))"; // end with [part or section]
		Matcher part_end_matcher = Pattern.compile(partEnd, Pattern.DOTALL).matcher(s);
		s = part_end_matcher.replaceAll("$1$2</part>\n");

		System.out.println("Identifying end of section");
		/* identify end of section */
		String sectionEnd = "(<section.*?>)(.*?)(?=(<section|<chapter|</document))";
		Matcher section_end_matcher = Pattern.compile(sectionEnd, Pattern.DOTALL).matcher(s);
		s = section_end_matcher.replaceAll("$1$2</section>\n");

		System.out.println("Identifying end of chapter");
		if (useChapter) {
			/* identify end of section */
			String chapterEnd = "(<chapter.*?>)(.*?)(?=(<chapter|</document))";
			Matcher chapter_end_matcher = Pattern.compile(chapterEnd, Pattern.DOTALL).matcher(s);
			s = chapter_end_matcher.replaceAll("$1$2</chapter>\n");
		}


		System.out.println("Parsing PDF to XML finished... ...");
		return s;
	}

	public String parseDocument(int endPage, String theme, String title, String edition) throws Exception {
		int startPage = 0;
		String text = readTextByArea(pdfDocument, startPage, endPage);
		return parseRequirement(text, theme, title, edition);
	}

	public static void main(String[] args) throws Exception {
		/*
		 * Remember: Have to manually define:
		 * 	* If the document has sub2-level (req on 2.2.2.2) or sub1-level (req on 2.2.2)
		 */

		String documentCode = "dnvgl-st-f101";
		String pdfPath = "/home/ole/Documents/dnv/ru-ship/" + documentCode + ".pdf";
		String outPath = "/home/ole/src/req_extractor/out/" + documentCode + ".xml";
		int lastPage = 319;
		String theme = "Submarine Pipeline Systems";
		String title = documentCode;
		String edition = "December 2017";
		PDFParser parser = new PDFParser(pdfPath, outPath);
		String xmlString = parser.parseDocument(lastPage, theme, title, edition);
		parser.writeXML(xmlString);

	}
}
