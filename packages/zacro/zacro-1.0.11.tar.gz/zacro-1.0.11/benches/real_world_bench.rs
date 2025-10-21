use criterion::{criterion_group, criterion_main, Criterion};
use zacro::XacroProcessor;

fn benchmark_real_world_file(c: &mut Criterion) {
    c.bench_function("real_world_file", |b| {
        b.iter(|| {
            // TODO: Add real-world URDF/xacro file processing benchmark
            let _processor = XacroProcessor::new();
        });
    });
}

criterion_group!(benches, benchmark_real_world_file);
criterion_main!(benches);
