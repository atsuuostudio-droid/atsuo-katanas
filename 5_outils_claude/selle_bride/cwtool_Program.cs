using System;
using System.IO;
using System.Xml;
using CodeWalker.GameFiles;
class P {
  static int Main(string[] a) {
    // a[0]=in.ycd.xml a[1]=out.ycd  |  "read" in.ycd out.xml
    if (a[0] == "conv") {   // conv Ydr|Ytd|RSC in.xml out
      var fmt = (MetaFormat)Enum.Parse(typeof(MetaFormat), a[1]);
      var d = new XmlDocument(); d.Load(a[2]);
      var bytes = XmlMeta.GetData(d, fmt, Path.GetDirectoryName(Path.GetFullPath(a[2])));
      if (bytes == null) { Console.WriteLine("ECHEC conversion"); return 1; }
      File.WriteAllBytes(a[3], bytes);
      Console.WriteLine(a[1] + " ok " + bytes.Length); return 0;
    }
    if (a[0] == "readytyp") {
      var t = new YtypFile(); t.Load(File.ReadAllBytes(a[1]));
      Console.WriteLine("ytyp: " + t.Name + " archetypes=" + (t.AllArchetypes?.Length ?? -1));
      if (t.AllArchetypes != null) foreach (var ar in t.AllArchetypes) Console.WriteLine("  " + ar.Name + " txd=" + ar.TextureDict + " r=" + ar.BSRadius);
      return 0;
    }
    if (a[0] == "readydr") {
      var y = new YdrFile(); y.Load(File.ReadAllBytes(a[1]));
      File.WriteAllText(a[2], MetaXml.GetXml(y, out string fn2, Path.GetDirectoryName(Path.GetFullPath(a[2]))));
      Console.WriteLine("ydr relu, modeles: " + (y.Drawable?.DrawableModels?.High?.Length ?? -1)); return 0;
    }
    if (a[0] == "read") {
      var y = new YcdFile(); RpfFile.LoadResourceFile(y, File.ReadAllBytes(a[1]), 46);
      File.WriteAllText(a[2], MetaXml.GetXml(y, out string fn));
      Console.WriteLine("xml ok " + fn); return 0;
    }
    var doc = new XmlDocument(); doc.Load(a[0]);
    var data = XmlMeta.GetData(doc, MetaFormat.Ycd, Path.GetDirectoryName(Path.GetFullPath(a[0])));
    File.WriteAllBytes(a[1], data);
    Console.WriteLine("ycd ok " + data.Length);
    var chk = new YcdFile(); RpfFile.LoadResourceFile(chk, data, 46);
    Console.WriteLine("relu: clips=" + (chk.ClipMap?.Count ?? -1) + " anims=" + (chk.AnimMap?.Count ?? -1));
    return 0;
  }
}
