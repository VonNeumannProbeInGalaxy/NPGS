#pragma once

#include <array>

#define GLM_FORCE_ALIGNED_GENTYPES
#include <glm/glm.hpp>
#include <glm/gtc/type_aligned.hpp>

#include "Engine/Core/Base/Base.h"

_NPGS_BEGIN
_RUNTIME_BEGIN
_GRAPHICS_BEGIN

// Vertex structs
// --------------
struct FTempVertex
{
    glm::vec3 Position;
    glm::vec2 TexCoord;
};

struct FVertex
{
    glm::vec3 Position;
    glm::vec3 Normal;
    glm::vec2 TexCoord;
    glm::vec3 Tangent;
    glm::vec3 Bitangent;
};

struct FInstanceData
{
    glm::mat4x4 Model{ glm::mat4x4(1.0f) };
};

struct FSkyboxVertex
{
    glm::vec3 Position;
};

struct FQuadVertex
{
    glm::vec2 Position;
    glm::vec2 TexCoord;
};

struct FQuadOnlyVertex
{
    glm::vec2 Position;
};

// Uniform buffer structs
// ----------------------
struct FGameArgs
{
    glm::aligned_vec2 Resolution;
    float             FovRadians;
    float             Time;
    float             TimeDelta;
    float             TimeRate;
};

struct FBlackHoleArgs
{
    glm::aligned_vec3 WorldUpView;
    glm::aligned_vec3 BlackHoleRelativePos;
    glm::vec3         BlackHoleRelativeDiskNormal;
    float             BlackHoleMassSol;
    float             Spin;
    float             Mu;
    float             AccretionRate;
    float             InnerRadiusLy;
    float             OuterRadiusLy;
};

struct FMatrices
{
    glm::aligned_mat4x4 View{ glm::mat4x4(1.0f) };
    glm::aligned_mat4x4 Projection{ glm::mat4x4(1.0f) };
    glm::aligned_mat4x4 LightSpaceMatrix{ glm::mat4x4(1.0f) };
};

struct FMvpMatrices
{
    glm::aligned_mat4x4 Model{ glm::mat4x4(1.0f) };
    glm::aligned_mat4x4 View{ glm::mat4x4(1.0f) };
    glm::aligned_mat4x4 Projection{ glm::mat4x4(1.0f) };
};

struct FMaterial
{
    alignas(16) float Shininess;
};

struct FLight
{
    glm::aligned_vec3 Position;
    glm::aligned_vec3 Ambient;
    glm::aligned_vec3 Diffuse;
    glm::aligned_vec3 Specular;
};

struct FLightMaterial
{
    FMaterial         Material;
    FLight            Light;
    glm::aligned_vec3 ViewPos;
};

struct FPbrArgs
{
    glm::vec3 Albedo;
    float     Metallic;
    float     Roughness;
    float     AmbientOcclusion;
};

struct FLightArgs
{
    glm::aligned_vec3 LightPos;
    glm::aligned_vec3 LightColor;
    glm::aligned_vec3 CameraPos;
};

_GRAPHICS_END
_RUNTIME_END
_NPGS_END
