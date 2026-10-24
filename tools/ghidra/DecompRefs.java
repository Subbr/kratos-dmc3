// Descompila as funções que referenciam cada endereço dado (e, com profundidade, quem as chama ou o que chamam).
// Uso (headless): -postScript DecompRefs.java <saida.c> <prof> <end1> [end2 ...]   end = hex sem 0x; prefixo f: = função
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.*;
import java.util.*;

public class DecompRefs extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] a = getScriptArgs();
        PrintWriter out = new PrintWriter(new FileWriter(a[0]));
        int depth = Integer.parseInt(a[1]);
        DecompInterface di = new DecompInterface();
        di.openProgram(currentProgram);
        Set<Function> todo = new LinkedHashSet<>();
        for (int i = 2; i < a.length; i++) {
            boolean fn = a[i].startsWith("f:");
            Address ad = toAddr(Long.parseLong(fn ? a[i].substring(2) : a[i], 16));
            if (fn) {
                Function f = getFunctionContaining(ad);
                if (f == null) {
                    // sem função criada pela análise: volta até o "addiu sp, sp, -N" (início típico de função MIPS)
                    Address s = ad;
                    for (int k = 0; k < 4096; k++, s = s.subtract(4)) {
                        int w = getInt(s);
                        if ((w >>> 16) == 0x27bd && (short) (w & 0xffff) < 0) break;
                    }
                    disassemble(s);
                    f = createFunction(s, null);
                    out.println("// função criada em " + s);
                }
                if (f != null) todo.add(f);
                continue;
            }
            for (Reference r : getReferencesTo(ad)) {
                Function f = getFunctionContaining(r.getFromAddress());
                out.println("// ref " + ad + " <- " + r.getFromAddress() + " em " + (f == null ? "?" : f.getName()));
                if (f != null) todo.add(f);
            }
        }
        Set<Function> done = new HashSet<>();
        for (int d = 0; d <= depth; d++) {
            Set<Function> next = new LinkedHashSet<>();
            for (Function f : todo) {
                if (!done.add(f)) continue;
                DecompileResults r = di.decompileFunction(f, 60, monitor);
                out.println("\n// ===== " + f.getName() + " @ " + f.getEntryPoint() + " (nível " + d + ")");
                out.println(r.decompileCompleted() ? r.getDecompiledFunction().getC() : "// falhou: " + r.getErrorMessage());
                for (Function c : f.getCalledFunctions(monitor)) next.add(c);
            }
            todo = next;
        }
        out.close();
    }
}
