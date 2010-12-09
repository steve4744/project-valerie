/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie;

import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.apache.commons.lang.StringEscapeUtils;
import valerie.controller.Controller;
import valerie.controller.Replace;
import valerie.tools.BoxInfo;

/**
 *
 * @author Admin
 */
public class MediaInfo implements Comparable<MediaInfo>{

    public static int alternativesMax = 30;

    public int ID = 0;

    public boolean isArchiv    = false;
    public boolean needsUpdate = false;
    public boolean Ignoring    = true;
    // This is only used in the sync process
    public boolean NotFound    = false;

    public boolean isMovie   = false;
    public boolean isSerie   = false;
    public boolean isEpisode = false;

    public boolean isEnigma2MetaRecording = false;

    public String LanguageOfPlot = "en";

    public String Path         = "";
    public String Filename     = "";
    public String Extension    = "";
    public String SearchString = "";

    public String Title = "";
    public int AlternativesCount = 0;
    public String AlternativTitles[] = new String[alternativesMax];
    /**
     * @deprecated
     */
    public String LocalTitle = "";
    public int    Year = 0;
    public String ImdbIdNull = "tt0000000";
    public String ImdbId     = ImdbIdNull;
    public String AlternativImdbs[] = new String[alternativesMax];
    public String TheTvDbIdNull = "0";
    public String TheTvDbId     = TheTvDbIdNull;
    public String TmDbIdNull = "0";
    public String TmDbId     = TmDbIdNull;

    public int    Runtime = 0;
    public String Resolution = "";
    public String Sound = "";
    public String Plot = "";
    /**
     * @deprecated
     */
    public String LocalPlot = "";
    public String Directors = "";
    public String Writers = "";
    public String Genres = "";
    public String Tag = "";
    /**
     * @deprecated
     */
    public String Releasedate = "";
    public int Popularity = 0;
    public int Season = -1;
    public int Episode = -1;


    public String Poster = "";
    public String Backdrop = "";
    public String Banner = "";

    //public int ref = -1;
    

    /**
     * @deprecated
     */
    public MediaInfo(String filename) {
        Path = filename;
        //File file = new File(filename);
        String[] path = filename.split("/");
        Filename = path[path.length - 1];
    }

    public MediaInfo(String path, String filename, String extension) {
        this.Path = path;
        this.Filename = filename;
        this.Extension = extension;
    }

    public MediaInfo() {
    }

    public boolean isEnigma2Recording(Controller pController, String name) {
        if(pController.get("BoxInfos") == null || pController.get("SelectedBoxInfo") == null)
            return false;
        BoxInfo[] pBoxInfos = (BoxInfo[])pController.get("BoxInfos");
        int selectedBoxInfo = (Integer)pController.get("SelectedBoxInfo");
        if (selectedBoxInfo < 0)
            return false;

        BoxInfo pBoxInfo = pBoxInfos[selectedBoxInfo];

        String[] entries = new valerie.tools.Network().sendCMD(pBoxInfo.IpAddress, "ls \"" + name + ".meta\"");
        if(entries.length > 0 && !entries[0].startsWith("ls:"))
            return true;

        return false;
    }

    public class Enimga2MetaInfo {
        public String MovieName = "";
        public String EpisodeName = "";
        public boolean IsMovie = false;
        public boolean IsEpisode = false;

        public Enimga2MetaInfo(String movieName, String episodeName) {
            MovieName = movieName.trim();
            EpisodeName = episodeName.trim();

            if(MovieName.equals(EpisodeName))
                IsMovie = true;
            else
                IsEpisode = true;
        }
    }

    public Enimga2MetaInfo getEnigma2RecordingName(Controller pController, String name) {
        if(pController.get("BoxInfos") == null || pController.get("SelectedBoxInfo") == null)
            return null;
        BoxInfo[] pBoxInfos = (BoxInfo[])pController.get("BoxInfos");
        int selectedBoxInfo = (Integer)pController.get("SelectedBoxInfo");
        if (selectedBoxInfo < 0)
            return null;

        BoxInfo pBoxInfo = pBoxInfos[selectedBoxInfo];

        String[] entries = new valerie.tools.Network().sendCMD(pBoxInfo.IpAddress, "cat \"" + name + ".meta\"");
        if(entries.length > 2 && !entries[0].startsWith("cat:")) {
            Enimga2MetaInfo e2info = new Enimga2MetaInfo(entries[1], entries[2]);
            return e2info;
        }
            
        return null;
    }

    public boolean isValerieInfoAvailable(Controller pController, String path) {
        if(pController.get("BoxInfos") == null || pController.get("SelectedBoxInfo") == null)
            return false;
        BoxInfo[] pBoxInfos = (BoxInfo[])pController.get("BoxInfos");
        int selectedBoxInfo = (Integer)pController.get("SelectedBoxInfo");
        if (selectedBoxInfo < 0)
            return false;

        BoxInfo pBoxInfo = pBoxInfos[selectedBoxInfo];

        String[] entries = new valerie.tools.Network().sendCMD(pBoxInfo.IpAddress, "ls \"" + path + "/valerie.info\"");
        if(entries.length > 0 && !entries[0].startsWith("ls:"))
            return true;

        return false;
    }

    public String getValerieInfo(Controller pController, String path) {
        if(pController.get("BoxInfos") == null || pController.get("SelectedBoxInfo") == null)
            return "";
        BoxInfo[] pBoxInfos = (BoxInfo[])pController.get("BoxInfos");
        int selectedBoxInfo = (Integer)pController.get("SelectedBoxInfo");
        if (selectedBoxInfo < 0)
            return "";

        BoxInfo pBoxInfo = pBoxInfos[selectedBoxInfo];

        String[] entries = new valerie.tools.Network().sendCMD(pBoxInfo.IpAddress, "cat \"" + path + "/valerie.info\"");
        if(entries.length > 0 && !entries[0].startsWith("cat:"))
            return entries[0];
        return "";
    }


    public boolean parse(Controller pController) {
        String absFilename = this.Path + "/" + this.Filename + "." + this.Extension;
        String name = this.Filename.toLowerCase();
        this.SearchString = name;

        //### Replacements PRE
        for (String[] replacement : Replace.replacements("pre")) {
            //#print "[pre] ", replacement[0], " --> ", replacement[1]
            this.SearchString = this.SearchString.replaceAll(replacement[0], replacement[1]).trim();
        }
        //#print ":-1: ", self.SearchString

        Matcher m;

        //###
        m = Pattern.compile("tt\\d{7}").matcher(name);
        if (m.find())
            this.ImdbId = m.group();

        //###
        m = Pattern.compile("\\s\\d{4}\\s").matcher(this.SearchString);
        if (m.find()) {
            String strYear = m.group().trim();
            int year = Integer.valueOf(strYear);
            if (year > 1940 && year < 2012) {
                this.Year = year;

                // removing year from searchstring
                this.SearchString = this.SearchString.replaceAll(strYear, " ");
                //this.SearchString = name.substring(0, m.start());
                }
        }

        //#print ":0: ", self.SearchString

        //###
        m = Pattern.compile("720p").matcher(name);
        if (m.find())
            this.Resolution = "720p";
        else {
            m = Pattern.compile("1080i").matcher(name);
            if (m.find())
                this.Resolution = "1080i";
            else {
                m = Pattern.compile("1080p").matcher(name);
                if (m.find())
                    this.Resolution = "1080p";
            }
        }

        //###
        m = Pattern.compile("dts").matcher(name);
        if (m.find())
            this.Sound = "dts";
        else {
            m = Pattern.compile("dd5").matcher(name);
           if (m.find())
                this.Sound = "ac3";
           else {
                m = Pattern.compile("ac3").matcher(name);
                if (m.find())
                    this.Sound = "ac3";
            }
        }

        //#nameConverted = name

        //#####
        //#####  s03e05
        //#####
        if(!this.isMovie) {
            if (this.Season == -1 || this.Episode == -1) {
                m = Pattern.compile("\\Ws\\d+\\s?e\\d+(\\D|$)").matcher(this.SearchString);
                if (m.find()) {
                    this.isEpisode = true; //this.isSerie = true; OK FOR BOX BUT NOT HERE
                    this.isMovie = false;
                    String group = m.group();
                    m = Pattern.compile("s\\d+").matcher(group.trim());
                    if (m.find()) {
                        this.Season = Integer.valueOf(m.group().substring(1).trim());
                    }
                    m = Pattern.compile("e\\d+").matcher(group.trim());
                    if (m.find()) {
                        this.Episode = Integer.valueOf(m.group().substring(1).trim());
                    }

                    this.SearchString = this.SearchString.replaceAll("s\\d+\\s?e\\d+.*", " ");
                }
            }

            //#####
            //#####  s03e05e06 s03e05-e06
            //#####

            if (this.Season == -1 || this.Episode == -1) {
                m = Pattern.compile("\\Ws(\\d+)\\s?e(\\d+)[-]?\\s?e?(\\d+)(\\D|$)").matcher(this.SearchString);
                if (m.find()) {
                    this.isEpisode = true; //this.isSerie = true; OK FOR BOX BUT NOT HERE
                    this.isMovie = false;
                    String group = m.group();
                    m = Pattern.compile("s\\d+").matcher(group.trim());
                    if (m.find()) {
                        this.Season = Integer.valueOf(m.group().substring(1).trim());
                    }
                    m = Pattern.compile("e\\d+").matcher(group.trim());
                    if (m.find()) {
                        this.Episode = Integer.valueOf(m.group().substring(1).trim());
                    }

                    this.SearchString = this.SearchString.replaceAll("s(\\d+)\\s?e(\\d+)[-]?\\s?e?(\\d+).*", " ");
                }
            }

            //#####
            //#####  3x05
            //#####

            if (this.Season == -1 || this.Episode == -1) {
                m = Pattern.compile("\\D\\d+x\\d+(\\D|$)").matcher(this.SearchString);
                if (m.find()) {
                    this.isEpisode = true; //this.isSerie = true; OK FOR BOX BUT NOT HERE
                    this.isMovie = false;

                    String group = m.group();
                    m = Pattern.compile("\\d+x").matcher(group);
                    if (m.find()) {
                        this.Season = Integer.valueOf(m.group().substring(0, m.group().length()-1).trim());
                    }

                    m = Pattern.compile("x\\d+").matcher(group);
                    if (m.find()) {
                        this.Episode = Integer.valueOf(m.group().substring(1).trim());
                    }

                    this.SearchString = this.SearchString.replaceAll("\\d+x\\d+.*", " ");
                }
            }

            //#####
            //#####  part 3
            //#####

            if (this.Season == -1 || this.Episode == -1) {
                m = Pattern.compile("\\W(part|pt)\\s?\\d+(\\D|$)").matcher(this.SearchString);
                if (m.find()) {
                    this.isEpisode = true; //this.isSerie = true; OK FOR BOX BUT NOT HERE
                    this.isMovie = false;

                    this.Season = 0;
                    String group = m.group();
                    m = Pattern.compile("\\s?\\d+").matcher(group);
                    if (m.find()) {
                        this.Episode = Integer.valueOf(m.group().trim());
                    }

                    this.SearchString = this.SearchString.replaceAll("(part|pt)\\s?\\d+.*", " ");
                }
            }

            //#####
            //#####  305
            //#####

            if (this.Season == -1 || this.Episode == -1) {

                String nameConverted = "";
                Character prevc = 'a';
                for (Character c : this.SearchString.toCharArray()) {
                    if ((Character.isDigit(prevc) && Character.isDigit(c)) || (Character.isDigit(prevc) == false && Character.isDigit(c) == false))
                        nameConverted += c;
                    else
                        nameConverted += " " + c;
                    prevc = c;
                }

                //print "[[[ ", nameConverted.encode('latin-1')

                nameConverted = nameConverted.trim();

                m = Pattern.compile("\\D\\d{3,4}(\\W|$)").matcher(nameConverted);
                if (m.find()) {
                    int se = -1;
                    int s = -1;
                    int e = -1;

                    String group = m.group();
                    m = Pattern.compile("\\D\\d{3,4}").matcher(group);
                    if (m.find()) {
                        se = Integer.valueOf(m.group().trim());
                    }

                    s = se / 100;
                    e = se % 100;

                    if ((s == 2 && e == 64 || s == 7 && e == 20 || s == 10 && e == 80 || s == 0 || s == 19 && e >= 40 || s == 20 && e <= 14) == false) {
                        this.isEpisode = true; //this.isSerie = true; OK FOR BOX BUT NOT HERE
                        this.isMovie = false;

                        this.Season = s;
                        this.Episode = e;

                        this.SearchString = nameConverted.replaceAll("\\d{3,4}.*", " ");
                    }
                }
            }
        }

        if (this.Extension.equals("ts") && this.isEnigma2Recording(pController, absFilename) == true) {
            Enimga2MetaInfo e2info = this.getEnigma2RecordingName(pController, absFilename);
            if(e2info != null) {
                if(e2info.IsMovie) {
                    this.SearchString = e2info.MovieName;
                    this.isMovie = true;
                    this.isEpisode = false;
                } else if (e2info.IsEpisode) {
                    this.SearchString = e2info.MovieName + ":: " + e2info.EpisodeName;
                    this.isMovie = false;
                    this.isEpisode = true;
                }
                //print ":: ", self.SearchString.encode('latin-1')
                this.isEnigma2MetaRecording = true;
                return true;
            }
        }

        /*if (this.isValerieInfoAvailable(pController, this.Path) == true) {
            this.SearchString = this.getValerieInfo(pController, this.Path).trim();
            if(this.SearchString.equals("ignore"))
                return false;
            //print ":: ", self.SearchString.encode('latin-1')
            return true;
        }*/

        if(!this.isEpisode)
            this.isMovie = true;

        //#print ":1: ", self.SearchString
        //### Replacements POST
        //this.SearchString = this.SearchString.replaceAll("[-]", " ");
        //this.SearchString = this.SearchString.replaceAll(" +", " ");
        //print ":2: ", self.SearchString.encode('latin-1')

        this.SearchString = this.SearchString.trim();

        String post = "post";
        if (this.isEpisode)
            post = "post_tv";
        else if (this.isMovie)
            post = "post_movie";

        for (String[] replacement : Replace.replacements(post)) {
            //#print "[" + post + "] ", replacement[0], " --> ", replacement[1]
            this.SearchString = this.SearchString.replaceAll(replacement[0], replacement[1]).trim();
        }

        this.SearchString = this.SearchString.trim();
        //print ":3: ", self.SearchString.encode('latin-1')

        return true;
    }



    public void importStr(String entry, boolean isMovie, boolean isSerie, boolean isEpisode) {

        this.isMovie = isMovie;
        this.isSerie = isSerie;
        this.isEpisode = isEpisode;


        try {
            String lines[] = entry.split("\n");

            for(String line : lines) {
                if(line.contains(": ")) {
                    String keys[] = line.split(": ", 2);
                    if(keys.length == 2) {

                        String key = keys[0].trim();
                        String value = keys[1].trim();

                        if(key.equals("TheTvDb"))
                            TheTvDbId = value;
                        else if(key.equals("TmDb"))
                            TmDbId = value;
                        else if(key.equals("ImdbId")) {
                            if(value.startsWith("tt"))
                                ImdbId = value;
                            else // Compatibility
                                ImdbId = String.format("tt%07d", Integer.valueOf(value));
                        }
                        else if(key.equals("Title"))
                            Title = value;
                        else if(key.equals("LocalTitle"))
                            LocalTitle =value;
                        else if(key.equals("Year"))
                            Year = Integer.valueOf(value);
                        else if(key.equals("Path")) {
                            String pathS = value.replace("//", "/"); // Remove double slash
                            String[] pathSplit = pathS.split("/");
                            String filenameS = pathSplit[pathSplit.length - 1];
                            pathS = pathS.substring(0, pathS.length() - filenameS.length() - 1);
                            String[] filenameSplit = filenameS.split("[.]");
                            String extensionS = filenameSplit[filenameSplit.length - 1];
                            filenameS = filenameS.substring(0, filenameS.length() - extensionS.length() - 1);
                            Path = pathS;
                            Filename = filenameS;
                            Extension = extensionS;
                        } else if (key.equals("Directors"))
                            Directors = value;
                        else if(key.equals("Writers"))
                            Writers = value;
                        else if(key.equals("Plot"))
                            Plot = value;
                        else if(key.equals("LocalPlot"))
                            LocalPlot = value;
                        else if(key.equals("Runtime"))
                            Runtime = Integer.valueOf(value);
                        else if(key.equals("Genres"))
                            Genres = value;
                        else if(key.equals("Tag"))
                            Tag = value;
                        else if(key.equals("Popularity"))
                            Popularity = Integer.valueOf(value);
                        else if(key.equals("Releasedate"))
                            Releasedate = value;
                        else if(key.equals("Season"))
                            Season = Integer.valueOf(value);
                        else if(key.equals("Episode"))
                            Episode = Integer.valueOf(value);
                    }
                }
            }

        }catch (Exception ex) {
            System.out.println(ex.toString());
        }
    }

    public void importDefined(String[] lines, boolean isMovie, boolean isSerie, boolean isEpisode) {
        this.isMovie = isMovie;
        this.isSerie = isSerie;
        this.isEpisode = isEpisode;

        if(this.isMovie) {
            this.ImdbId = lines[0];
            this.Title = lines[1];
            this.Tag = lines[2];
            this.Year = Integer.valueOf(lines[3]);

            this.Path = lines[4];
            this.Filename = lines[5];
            this.Extension = lines[6];

            this.Plot = lines[7];
            this.Runtime = Integer.valueOf(lines[8]);
            this.Popularity = Integer.valueOf(lines[9]);

            this.Genres = lines[10];
        }
        else if(this.isSerie) {
            this.ImdbId = lines[0];
            this.TheTvDbId = lines[1];
            this.Title = lines[2];
            this.Tag = lines[3];
            this.Year = Integer.valueOf(lines[4]);

            this.Plot = lines[5];
            this.Runtime = Integer.valueOf(lines[6]);
            this.Popularity = Integer.valueOf(lines[7]);

            this.Genres = lines[8];
        }
        else if(this.isEpisode) {
            this.TheTvDbId = lines[0];
            this.Title = lines[1];
            this.Year = Integer.valueOf(lines[2]);

            this.Path = lines[3];
            this.Filename = lines[4];
            this.Extension = lines[5];

            this.Season = Integer.valueOf(lines[6]);
            this.Episode = Integer.valueOf(lines[7]);

            this.Plot = lines[8];
            this.Runtime = Integer.valueOf(lines[9]);
            this.Popularity = Integer.valueOf(lines[10]);
        
            this.Genres = lines[11];
        }
    }

    public String exportStr() {
        return  "---BEGIN---\n" +
                (isEpisode||isSerie?("TheTvDb: " + TheTvDbId + "\n"):"") +
                (isMovie?("TheTvDb: " + TmDbId + "\n"):"") +
                "ImdbId: " + ImdbId + "\n" +
                "Title: " + Title + "\n" +
                "LocalTitle: " + LocalTitle + "\n" +
                "Year: " + Year + "\n" +
                (!isSerie?("Path: " + Path + "/" + Filename + "." + Extension + "\n"):"") +
                "Directors: " + Directors + "\n" +
                "Writers: " + Writers + "\n" +
                "Plot: " + Plot + "\n" +
                "LocalPlot: " + LocalPlot + "\n" +
                "Runtime: " + Runtime + "\n" +
                "Genres: " + Genres + "\n" +
                "Releasedate: " + Releasedate + "\n" +
                "Tag: " + Tag + "\n" +
                "Popularity: " + Popularity + "\n" +
                (isEpisode?("Season: " + Season + "\n"):"") +
                (isEpisode?("Episode: " + Episode + "\n"):"") +
                "----END----\n\n";
    }

    public String exportDefined() {
        String stri = "";
        if(this.isMovie) {
            stri += this.ImdbId + "\n";
            stri += this.Title + "\n";
            stri += this.Tag + "\n";
            stri += this.Year + "\n";

            stri += this.Path + "\n";
            stri += this.Filename + "\n";
            stri += this.Extension + "\n";

            stri += this.Plot + "\n";
            stri += this.Runtime + "\n";
            stri += this.Popularity + "\n";

            stri += this.Genres + "\n";
        }
        else if(this.isSerie) {
            stri += this.ImdbId + "\n";
            stri += this.TheTvDbId + "\n";
            stri += this.Title + "\n";
            stri += this.Tag + "\n";
            stri += this.Year + "\n";

            stri += this.Plot + "\n";
            stri += this.Runtime + "\n";
            stri += this.Popularity + "\n";

            stri += this.Genres + "\n";
        }
        else if(this.isEpisode) {
            stri += this.TheTvDbId + "\n";
            stri += this.Title + "\n";
            stri += this.Year + "\n";

            stri += this.Path + "\n";
            stri += this.Filename + "\n";
            stri += this.Extension + "\n";

            stri += this.Season + "\n";
            stri += this.Episode + "\n";

            stri += this.Plot + "\n";
            stri += this.Runtime + "\n";
            stri += this.Popularity + "\n";

            stri += this.Genres + "\n";
        }
        return stri;
    }

    public String cleanString(String str){ /// "Lange Beine, kurze L&#xFC;gen (und ein F&#xFC;nkchen Wahrheit...)"
        str = StringEscapeUtils.unescapeHtml(str);

    	return str;
    }
    public void checkStrings() {

        Title = cleanString(Title);
        LocalTitle = cleanString(LocalTitle);
        Plot = cleanString(Plot);
        LocalPlot = cleanString(LocalPlot);
        Directors = cleanString(Directors);
        Writers = cleanString(Writers);
        Genres = cleanString(Genres);
        Tag = cleanString(Tag);

        for(int i = 0; i < alternativesMax; i++)
            AlternativTitles[i] = cleanString(AlternativTitles[i]);
    }

    @Override
    public String toString() {
        //if(Imdb > 0)
        return  (isEpisode||isSerie?("TheTvDb: " + TheTvDbId + "\n"):"") +
                (isMovie?("TheTvDb: " + TmDbId + "\n"):"") +
                "ImdbId: " + ImdbId + "\n" +
                //"Title: " + Title + "\n" +
                //"LocalTitle: " + LocalTitle + "\n" +
                "Year: " + Year + "\n" +
                //"Filename: " + Filename + "\n" +
                (!isSerie?("Path: " + Path + "/" + Filename + "." + Extension + "\n"):"") +
                //"Directors: " + Directors + "\n" +
                //"Writers: " + Writers + "\n" +
                //"Plot: " + Plot + "\n" +
                //"LocalPlot: " + LocalPlot + "\n" +
                "Runtime: " + Runtime + "\n" +
                "Genres: " + Genres + "\n" +
                //"Releasedate: " + Releasedate + "\n" +
                //"Tag: " + Tag + "\n" +
                "Popularity: " + Popularity + "\n" +
                (isEpisode?("Season: " + Season + "\n"):"") +
                (isEpisode?("Episode: " + Episode + "\n"):"");
        //else
        //    return "";
    }

    @Override
    public MediaInfo clone() {
        MediaInfo rtv = new MediaInfo(Filename);

        rtv.isMovie = isMovie;
        rtv.isSerie = isSerie;
        rtv.isEpisode = isEpisode;
        rtv.Filename = Filename;
        rtv.Path = Path;
        rtv.SearchString = SearchString;
        rtv.Title = Title;
        rtv.LocalTitle = LocalTitle;
        rtv.Year = Year;
        rtv.ImdbId = ImdbId;
        rtv.Poster = Poster;
        rtv.Backdrop = Backdrop;
        rtv.Banner = Banner;
        rtv.Runtime = Runtime;
        rtv.Plot = Plot;
        rtv.LocalPlot = LocalPlot;
        rtv.Directors = Directors;
        rtv.Writers = Writers;
        rtv.Genres = Genres;
        rtv.Tag = Tag;
        rtv.Popularity = Popularity;
        rtv.Season = Season;
        rtv.Episode = Episode;
        rtv.TheTvDbId = TheTvDbId;
        rtv.TmDbId = TmDbId;
        rtv.Releasedate = Releasedate;
        
        rtv.Ignoring = Ignoring;
        rtv.isArchiv = isArchiv;
        rtv.needsUpdate = needsUpdate;
        return rtv;
    }

    public int compareTo(MediaInfo o) {
        if (this.isMovie || this.isSerie)
         return this.Title.compareTo(o.Title);
        else if (this.isEpisode)
            return (this.Season*100+this.Episode)-(o.Season*100+o.Episode);
        else
            return 0;
    }


}
