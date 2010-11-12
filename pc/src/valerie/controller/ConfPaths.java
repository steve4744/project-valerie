/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.controller;

import java.util.Arrays;
import java.util.LinkedList;
import valerie.Utf8;
import valerie.tools.Path;

/**
 *
 * @author i7
 */
public final class ConfPaths {



    

    private String Filter = null;
    private LinkedList<Path> Paths = new LinkedList<Path>();

    public ConfPaths() {
        load();
    }

    public void clear() {
        Filter = null;
        Paths.clear();
    }

    public void load() {
        Utf8 conf = new Utf8("conf\\paths.conf", "r");
        for(String line : conf.read().split("\n")) {
            if(Filter == null) Filter = line;
            else Paths.add(new Path(line));
        }
        conf.close();
    }

    public void reload() {
        clear();
        load();
    }

    public void save() {
        Utf8 conf = new Utf8("conf\\paths.conf", "w");
        conf.write(this.Filter + "\n");
        for(Path path : this.Paths) {
            conf.write(path + "\n");
        }
        conf.close();
    }

    public String getFilter() {
        return this.Filter;
    }

    public void setFilter(String filter) {
        this.Filter = filter;
    }

    public Path[] getPaths() {
        return this.Paths.toArray(new Path[1]);
    }

    public void setPaths(Path[] paths) {
        this.Paths = new LinkedList<Path>(Arrays.asList(paths));
    }
}
