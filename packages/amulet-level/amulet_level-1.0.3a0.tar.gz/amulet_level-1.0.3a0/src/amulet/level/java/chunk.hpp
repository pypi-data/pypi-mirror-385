#pragma once

#include <map>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

#include <amulet/nbt/tag/named_tag.hpp>

#include <amulet/core/biome/biome.hpp>
#include <amulet/core/block/block.hpp>
#include <amulet/core/chunk/chunk.hpp>
#include <amulet/core/chunk/component/block_component.hpp>

#include <amulet/level/dll.hpp>

#include "chunk_components/data_version_component.hpp"
#include "chunk_components/java_raw_chunk_component.hpp"

namespace Amulet {
using JavaRawChunk = std::map<std::string, Amulet::NBT::NamedTag>;

class JavaChunk : public Chunk { };

class JavaChunkNA : public ChunkComponentHelper<
                        JavaChunk,
                        JavaRawChunkComponent,
                        DataVersionComponent,
                        // LastUpdateComponent,
                        // JavaLegacyVersionComponent,
                        BlockComponent //,
                        // BlockEntityComponent,
                        // EntityComponent,
                        // Biome2DComponent,
                        // Height2DComponent,
                        > {
public:
    AMULET_LEVEL_EXPORT static const std::string ChunkID;

    std::string get_chunk_id() const override;

    using ChunkComponentHelper::ChunkComponentHelper;
    AMULET_LEVEL_EXPORT JavaChunkNA(
        const BlockStack& default_block,
        const Biome& default_biome);
};

class JavaChunk0 : public ChunkComponentHelper<
                       JavaChunk,
                       JavaRawChunkComponent,
                       DataVersionComponent,
                       // LastUpdateComponent,
                       // TerrainPopulatedComponent,
                       // LightPopulatedComponent,
                       BlockComponent //,
                       // BlockEntityComponent,
                       // EntityComponent,
                       // Biome2DComponent,
                       // Height2DComponent,
                       > {
public:
    AMULET_LEVEL_EXPORT static const std::string ChunkID;

    std::string get_chunk_id() const override;

    using ChunkComponentHelper::ChunkComponentHelper;
    AMULET_LEVEL_EXPORT JavaChunk0(
        std::int64_t data_version,
        const BlockStack& default_block,
        const Biome& default_biome);
};

class JavaChunk1444 : public ChunkComponentHelper<
                          JavaChunk,
                          JavaRawChunkComponent,
                          DataVersionComponent,
                          // LastUpdateComponent,
                          // StatusStringComponent,
                          BlockComponent //,
                          // BlockEntityComponent,
                          // EntityComponent,
                          // Biome2DComponent,
                          // Height2DComponent,
                          > {
public:
    AMULET_LEVEL_EXPORT static const std::string ChunkID;

    std::string get_chunk_id() const override;

    using ChunkComponentHelper::ChunkComponentHelper;
    AMULET_LEVEL_EXPORT JavaChunk1444(
        std::int64_t data_version,
        const BlockStack& default_block,
        const Biome& default_biome);
};

class JavaChunk1466 : public ChunkComponentHelper<
                          JavaChunk,
                          JavaRawChunkComponent,
                          DataVersionComponent,
                          // LastUpdateComponent,
                          // StatusStringComponent,
                          BlockComponent //,
                          // BlockEntityComponent,
                          // EntityComponent,
                          // Biome2DComponent,
                          // NamedHeight2DComponent,
                          > {
public:
    AMULET_LEVEL_EXPORT static const std::string ChunkID;

    std::string get_chunk_id() const override;

    using ChunkComponentHelper::ChunkComponentHelper;
    AMULET_LEVEL_EXPORT JavaChunk1466(
        std::int64_t data_version,
        const BlockStack& default_block,
        const Biome& default_biome);
};

class JavaChunk2203 : public ChunkComponentHelper<
                          JavaChunk,
                          JavaRawChunkComponent,
                          DataVersionComponent,
                          // LastUpdateComponent,
                          // StatusStringComponent,
                          BlockComponent //,
                          // BlockEntityComponent,
                          // EntityComponent,
                          // Biome3DComponent,
                          // NamedHeight2DComponent,
                          > {
public:
    AMULET_LEVEL_EXPORT static const std::string ChunkID;

    std::string get_chunk_id() const override;

    using ChunkComponentHelper::ChunkComponentHelper;
    AMULET_LEVEL_EXPORT JavaChunk2203(
        std::int64_t data_version,
        const BlockStack& default_block,
        const Biome& default_biome);
};

namespace detail {
    // Get a null chunk instance for the given chunk id.
    std::unique_ptr<JavaChunk> get_java_null_chunk(const std::string& chunk_id);

    // Get the chunk's identifier.
    std::string get_java_chunk_id(const JavaChunk& chunk);
} // namespace detail

}
